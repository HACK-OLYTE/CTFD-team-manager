import os

from flask import Blueprint, redirect, render_template, request, url_for, send_from_directory

from CTFd.cache import clear_standings, clear_team_session, clear_user_session
from CTFd.models import Submissions, Users, db
from CTFd.plugins import register_plugin_script
from CTFd.utils import config as ctfd_config
from CTFd.utils.decorators import authed_only, require_verified_emails
from CTFd.utils.helpers import error_for, get_errors, get_infos
from CTFd.utils.user import get_current_team, get_current_user


def load(app):
    _register_routes(app)
    register_plugin_script("/team-manager/assets/disband_redirect.js")


def _register_routes(app):
    bp = Blueprint("team_manager", __name__, template_folder="templates")

    # Serve plugin static assets
    @bp.route("/team-manager/assets/<path:filename>")
    def serve_asset(filename):
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        return send_from_directory(assets_dir, filename)

    # GET/POST /teams/leave
    @bp.route("/teams/leave", methods=["GET", "POST"])
    @authed_only
    @require_verified_emails
    def leave_team():
        if not ctfd_config.is_teams_mode():
            return redirect(url_for("challenges.listing"))

        user = get_current_user()
        team = get_current_team()

        if not team:
            return redirect(url_for("challenges.listing"))

        is_captain = team.captain_id == user.id
        other_members = [m for m in team.members if m.id != user.id]
        has_other_members = bool(other_members)

        infos = get_infos()
        errors = get_errors()

        if request.method == "POST":
            # Validate successor if captain
            captain_error = ""
            new_captain_id = None
            if is_captain and has_other_members:
                raw = request.form.get("new_captain_id", "").strip()
                valid_ids = {m.id for m in other_members}
                try:
                    new_captain_id = int(raw)
                    if new_captain_id not in valid_ids:
                        raise ValueError()
                except (ValueError, TypeError):
                    captain_error = "Please select a valid captain."

            if captain_error:
                return render_template(
                    "leave_team.html",
                    team=team, other_members=other_members,
                    is_captain=is_captain, has_other_members=has_other_members,
                    captain_error=captain_error,
                    infos=infos, errors=errors,
                )

            try:
                user_id = user.id
                team_id = team.id

                # Standard CTFd behavior: delete all submissions
                Submissions.query.filter_by(user_id=user_id).delete()

                # Transfer captaincy
                if is_captain and has_other_members and new_captain_id:
                    team.captain_id = new_captain_id

                team.members.remove(user)

                if not has_other_members:
                    db.session.delete(team)

                db.session.commit()

                clear_user_session(user_id=user_id)
                clear_team_session(team_id=team_id)
                clear_standings()

                return redirect(url_for("challenges.listing"))

            except Exception:
                db.session.rollback()
                error_for("team_manager.leave_team", "A technical error occurred. Please contact an administrator.")
                return redirect(url_for("team_manager.leave_team"))

        return render_template(
            "leave_team.html",
            team=team, other_members=other_members,
            is_captain=is_captain, has_other_members=has_other_members,
            captain_error="",
            infos=infos, errors=errors,
        )

    # POST /teams/kick-member
    @bp.route("/teams/kick-member", methods=["POST"])
    @authed_only
    @require_verified_emails
    def kick_member():
        if not ctfd_config.is_teams_mode():
            return redirect(url_for("challenges.listing"))

        user = get_current_user()
        team = get_current_team()

        if not team:
            return redirect(url_for("challenges.listing"))

        if team.captain_id != user.id:
            error_for("team_manager.leave_team", "Only the captain can kick members.")
            return redirect(url_for("team_manager.leave_team"))

        raw = request.form.get("member_id", "").strip()
        valid_ids = {m.id for m in team.members if m.id != user.id}
        try:
            member_id = int(raw)
            if member_id not in valid_ids:
                raise ValueError()
        except (ValueError, TypeError):
            error_for("team_manager.leave_team", "Invalid member.")
            return redirect(url_for("team_manager.leave_team"))

        target = Users.query.filter_by(id=member_id).first_or_404()

        try:
            # Standard CTFd behavior: delete all submissions for the member
            Submissions.query.filter_by(user_id=member_id).delete()
            team.members.remove(target)
            db.session.commit()

            clear_user_session(user_id=member_id)
            clear_team_session(team_id=team.id)
            clear_standings()

        except Exception:
            db.session.rollback()
            error_for("team_manager.leave_team", "A technical error occurred. Please contact an administrator.")

        return redirect(url_for("team_manager.leave_team"))

    # POST /teams/dissolve
    @bp.route("/teams/dissolve", methods=["POST"])
    @authed_only
    @require_verified_emails
    def dissolve_team():
        if not ctfd_config.is_teams_mode():
            return redirect(url_for("challenges.listing"))

        user = get_current_user()
        team = get_current_team()

        if not team:
            return redirect(url_for("challenges.listing"))

        if team.captain_id != user.id:
            error_for("team_manager.leave_team", "Only the captain can disband the team.")
            return redirect(url_for("team_manager.leave_team"))

        typed_name = request.form.get("confirm_name", "").strip()
        if typed_name != team.name:
            error_for("team_manager.leave_team", "Team name does not match. Disbanding cancelled.")
            return redirect(url_for("team_manager.leave_team"))

        try:
            team_id = team.id
            all_member_ids = [m.id for m in team.members]

            # Standard CTFd behavior: delete all submissions for all members
            for member_id in all_member_ids:
                Submissions.query.filter_by(user_id=member_id).delete()

            team.members = []
            db.session.delete(team)
            db.session.commit()

            for member_id in all_member_ids:
                clear_user_session(user_id=member_id)
            clear_team_session(team_id=team_id)
            clear_standings()

            return redirect(url_for("challenges.listing"))

        except Exception:
            db.session.rollback()
            error_for("team_manager.leave_team", "A technical error occurred. Please contact an administrator.")
            return redirect(url_for("team_manager.leave_team"))

    app.register_blueprint(bp)

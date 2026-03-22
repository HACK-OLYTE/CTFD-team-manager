# CTFd Team Manager

A CTFd plugin that gives players full autonomy over their team — **no admin intervention needed**. Players can leave on their own, captains can kick members or hand over leadership, and disband the team entirely if needed.

## Why this plugin?

By default, CTFd does not allow players to leave a team or kick members without going through an administrator. During a CTF event, this creates unnecessary friction and overhead for the admin team. This plugin adds a self-service `/teams/leave` page where players and captains manage their team directly.

## Features

### For all players
- **Leave the team** autonomously via `/teams/leave`
- Warned upfront that all their submissions and solves will be deleted
- If they are the last member, the team is automatically disbanded

### For captains
- **Transfer captaincy** before leaving — must select a successor from current members
- **Kick a member** from the team (their solves are deleted)
- **Disband the team** entirely (Danger Zone) — requires typing the team name to confirm; all members are removed and all solves deleted

## How it works

| Route | Method | Description |
|---|---|---|
| `/teams/leave` | GET / POST | Leave the team (with optional captain transfer) |
| `/teams/kick-member` | POST | Captain kicks a member |
| `/teams/dissolve` | POST | Captain permanently disbands the team |

All actions require the user to be authenticated and have a verified email. Admin and plugin routes are never affected.

## Installation

Copy the `ctfd-team-manager` folder into your CTFd `plugins/` directory:

```
CTFd/plugins/ctfd-team-manager/
```

Restart CTFd. The routes are available immediately — you can link to `/teams/leave` from your theme or announcements.

> This plugin only works when CTFd is running in **Teams mode**.

## Dependencies

- CTFd >= v3.x
- CTFd running in **Teams mode**
- Compatible with Docker and local installations
- An up-to-date browser with JavaScript enabled
- CTFd theme: Core-beta

## Support

For any question or issue, open an [issue](https://github.com/votre-utilisateur/ctfd-team-manager/issues).
Or contact us on the Hack'olyte association website: [contact](https://hackolyte.fr/contact/).

## Contributing

Contributions are welcome!
You can:

- Report bugs
- Suggest new features
- Submit pull requests

## License

This plugin is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

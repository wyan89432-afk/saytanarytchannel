# Saytanar YouTube → Telegram Bot

Automatically checks `@saytanar68` for new uploads every 5 minutes and posts each new video to the Telegram group `@happydayfor`.

## Required GitHub Secret

In the repository, open **Settings → Secrets and variables → Actions → New repository secret** and create:

- `TELEGRAM_BOT_TOKEN` = the token from **@BotFather** for `@Saytanar_bot`

The token is intentionally not stored in this repository.

## Telegram requirements

- Add `@Saytanar_bot` to the `@happydayfor` group.
- Give the bot permission to send messages.
- Keep the bot token only in GitHub Secrets.

The workflow runs every 5 minutes and also supports manual **Run workflow** from the Actions tab.

## Important

The repository code cannot be deleted after deployment because GitHub Actions needs the workflow to continue running. The bot code therefore remains in the repository, while the bot token stays hidden in GitHub Secrets.

It looks like there's a small mismatch in the `tmux` session name.

The `manage.sh` script is designed to create a `tmux` session named **`rfibot`**, not `rfibot-session`.

Could you please try to attach to the correct session name:
```bash
tmux attach -t rfibot
```
(Remember you can detach by pressing `Ctrl+b` then `d`).

Also, please run `tmux ls` again and share its output to confirm the exact name of any sessions that were created. This will help verify if `tmux new-session` ran correctly.
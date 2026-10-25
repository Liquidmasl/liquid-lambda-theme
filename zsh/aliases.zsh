# Optional zsh extras from the upstream rice: lsd / bat / nvim aliases and the
# starship prompt. The colours live in the generated zsh/lambda.zsh.
#
# Source it from your ~/.zshrc if you want them:
#   source /path/to/liquid-lambda-theme/zsh/aliases.zsh

if (( $+commands[lsd] )); then
    alias ls='lsd'
    alias la='lsd -a'
    alias ll='lsd -l'
    alias lla='lsd -la'
fi

# Debian/Ubuntu ship bat as batcat
if (( $+commands[batcat] )); then
    alias cat='batcat'
elif (( $+commands[bat] )); then
    alias cat='bat'
fi

(( $+commands[cosmic-edit] )) && alias edit='cosmic-edit'

if (( $+commands[nvim] )); then
    alias vi='nvim'
    alias vim='nvim'
    alias v='nvim'
fi

# needs ZSH_THEME="" with oh-my-zsh
(( $+commands[starship] )) && eval "$(starship init zsh)"

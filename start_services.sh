#!/bin/bash

SESSION_NAME="ppt-watcher"

# Check if session exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
  # Create new session
  tmux new-session -d -s $SESSION_NAME -n backend
  
  # Setup backend window
  tmux send-keys -t $SESSION_NAME:backend "cd ~/site-watcher/backend" C-m
  tmux send-keys -t $SESSION_NAME:backend "source venv/bin/activate" C-m
  tmux send-keys -t $SESSION_NAME:backend "python app.py" C-m
  
  # Setup frontend window
  tmux new-window -t $SESSION_NAME -n frontend
  tmux send-keys -t $SESSION_NAME:frontend "cd ~/site-watcher/frontend" C-m
  tmux send-keys -t $SESSION_NAME:frontend "serve -s dist -l 5173" C-m
  
  echo "Started PTT Watcher in tmux session '$SESSION_NAME'"
else
  echo "Session '$SESSION_NAME' already exists. Attaching..."
fi

# Attach to session
# tmux attach -t $SESSION_NAME

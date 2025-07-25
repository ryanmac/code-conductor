# Claude Code Setup Prompt for Code Conductor

Copy and paste the following prompt into Claude Code to automatically set up or upgrade Code Conductor in your project:

---

## For New Installation:

```
I need you to set up Code Conductor in this project to help coordinate multiple AI agents working on the codebase. 

Please:
1. Run the installation command: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
2. When prompted, choose the appropriate options based on the project
3. After installation completes, run the initial discovery task: ./conductor start dev
4. When you claim the [INIT] task, thoroughly explore the project documentation and create a comprehensive documentation map
5. After completing the [INIT] task, use ./conductor complete to submit your work

This will set up automated task management, AI code reviews, and agent coordination for the project.
```

## For Upgrading Existing Installation:

```
I need you to upgrade Code Conductor to the latest version in this project.

Please:
1. Run the upgrade command: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
2. When prompted about the existing installation, choose option 1 (Upgrade)
3. Review the upgrade summary to see what's new
4. After upgrade completes, run: ./conductor status to verify everything is working
5. If there are any issues, run: ./conductor diagnose

This will update all core scripts while preserving your configurations and existing work.
```

## For Complete Automation (New Projects):

```
I want you to fully set up Code Conductor in this project and complete the initial documentation discovery task automatically.

Execute these commands in sequence:

# Install Code Conductor
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)

# For all prompts during installation:
- If asked about existing installation: Choose option 2 (Reinstall) if needed
- For copying examples: Press Enter (Yes)
- For agent roles: Type numbers for roles relevant to this project, then 0
- For demo tasks: Press n (No - we'll create real tasks)
- For auto-commit: Press Enter (Yes)
- For environment: Choose 3 (IDE)
- For starting dev agent: Press Enter (Yes)

After installation completes and the dev agent starts:
1. You should automatically claim the [INIT] discovery task
2. Thoroughly explore all documentation, README files, docs folders, wikis
3. Create a comprehensive .conductor/documentation-map.yaml with your findings
4. Include proposed development tasks based on the project's needs
5. Run ./conductor complete to submit the documentation map

This will fully set up the project with Code Conductor and create an actionable task list for development.
```

## For Specific Environments:

### VSCode/Cursor/Windsurf Users:
```
Set up Code Conductor for IDE-based development. Run: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh) and select option 3 (IDE) when prompted for environment. After setup, use ./conductor start [role] to begin work on tasks.
```

### Terminal/Warp Users:
```
Set up Code Conductor for terminal-based development. Run: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh) and select option 2 (Terminal) when prompted for environment. After setup, use ./conductor start [role] to begin work on tasks.
```

### macOS Conductor App Users:
```
Set up Code Conductor for the Conductor app. Run: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh) and select option 1 (Conductor) when prompted for environment. After setup, open the Conductor app and add this project as a workspace.
```

## Troubleshooting Prompt:

```
Code Conductor seems to have issues. Please diagnose and fix:

1. Run: ./conductor diagnose
2. Fix any reported issues:
   - If GitHub CLI not authenticated: Run gh auth login
   - If not in git repo: Ensure you're in the project root
   - If missing config: Re-run the installer
3. Run: ./conductor recover if there are worktree or task state issues
4. Check recent changes: git log .conductor/ --oneline -10
5. If all else fails, run the installer again and choose "Upgrade" to refresh the installation

Report the specific error messages you see so I can help resolve them.
```

## Quick Task Management:

```
Help me work on Code Conductor tasks:

1. Show available tasks: ./conductor tasks
2. Start work on highest priority: ./conductor start dev
3. Update progress: ./conductor progress (then describe what you've done)
4. Complete current task: ./conductor complete
5. Check status anytime: ./conductor status

Focus on tasks that match your capabilities and complete them autonomously.
```
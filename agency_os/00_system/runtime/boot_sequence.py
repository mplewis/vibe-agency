"""Boot Sequence - Main entry point for system-boot.sh → vibe-cli boot

Orchestrates the conveyor belt:
1. Context Loader → Collect signals
2. Playbook Engine → Route to task
3. Prompt Composer → Compose final prompt
"""

import sys
from pathlib import Path
from typing import Optional

from context_loader import ContextLoader
from playbook_engine import PlaybookEngine
from prompt_composer import PromptComposer


class BootSequence:
    """Main entry point for system boot"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.context_loader = ContextLoader(self.project_root)
        self.playbook_engine = PlaybookEngine()
        self.prompt_composer = PromptComposer()
    
    def run(self, user_input: Optional[str] = None):
        """Execute the boot sequence"""
        
        # Conveyor Belt 1: Load Context
        print("🔄 Loading context...", file=sys.stderr)
        context = self.context_loader.load()
        
        # Conveyor Belt 2: Route to Task
        print("🎯 Routing to task...", file=sys.stderr)
        route = self.playbook_engine.route(user_input or "", context)
        
        # Conveyor Belt 3: Compose Prompt
        print("📝 Composing prompt...", file=sys.stderr)
        prompt = self.prompt_composer.compose(route.task, context)
        
        # Display dashboard
        self._display_dashboard(context, route)
        
        # Output prompt for STEWARD
        print("\n" + "=" * 80, file=sys.stderr)
        print(prompt)
        print("=" * 80 + "\n", file=sys.stderr)
    
    def _check_git_sync(self) -> dict:
        """Check if repo is behind remote - graceful fallback if git fails"""
        try:
            import subprocess
            
            # Fetch latest refs (non-destructive)
            subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=self.project_root,
                capture_output=True,
                timeout=5,
                check=False  # Don't fail if fetch fails
            )
            
            # Count commits behind
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD..origin/main'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            
            commits_behind = int(result.stdout.strip())
            return {
                'behind': commits_behind > 0,
                'commits_behind': commits_behind,
                'status': 'sync_needed' if commits_behind > 0 else 'up_to_date'
            }
        except Exception as e:
            # Graceful fallback - don't break boot
            return {
                'behind': False,
                'commits_behind': 0,
                'status': 'unknown',
                'error': str(e)
            }
    
    def _display_dashboard(self, context: dict, route) -> None:
        """Display system status dashboard"""
        
        session = context.get('session', {})
        git = context.get('git', {})
        tests = context.get('tests', {})
        env = context.get('environment', {})
        
        # Check git sync status
        sync_status = self._check_git_sync()
        
        # Calculate status indicators
        test_emoji = '✅' if tests.get('failing_count', 0) == 0 else '❌'
        git_emoji = '✅' if git.get('uncommitted', 0) == 0 else '⚠️'
        env_emoji = '✅' if env.get('status') == 'ready' else '⚠️'
        sync_emoji = '✅' if not sync_status.get('behind') else '⚠️'
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🤖 VIBE AGENCY SYSTEM BOOT                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 SYSTEM STATUS
  {test_emoji} Tests: {tests.get('failing_count', 0)} failing, {tests.get('status', 'unknown')}
  {git_emoji} Git: {git.get('uncommitted', 0)} uncommitted files on '{git.get('branch', 'unknown')}'
  {sync_emoji} Sync: {sync_status.get('commits_behind', 0)} commits behind origin/main
  {env_emoji} Environment: {env.get('status', 'unknown')}

"""
        
        # Add sync suggestion if behind
        if sync_status.get('behind'):
            behind_count = sync_status.get('commits_behind', 0)
            dashboard += f"""⚠️  REPO OUT OF SYNC ({behind_count} commits behind)
  To sync: git pull origin main
  
"""
        
        dashboard += f"""
🎯 RECOMMENDED TASK
  Task: {route.task.upper()}
  Description: {route.description}
  Confidence: {route.confidence}
  Reason: {route.source}

📋 PROJECT STATE
  Phase: {session.get('phase', 'UNKNOWN')}
  Last Task: {session.get('last_task', 'none')}
  Backlog Items: {len(session.get('backlog', []))}

"""
        
        # Show available routes if in suggestion mode
        if route.confidence == 'suggested':
            routes = self.playbook_engine.list_available_routes()
            dashboard += "\n💡 AVAILABLE ROUTES:\n"
            for r in routes[:5]:
                examples = ', '.join(r['examples'][:2])
                dashboard += f"  - {r['name']}: {r['description']}\n"
                dashboard += f"    Examples: {examples}\n"
        
        print(dashboard, file=sys.stderr)
    
    def show_routes(self) -> None:
        """Show all available playbook routes"""
        routes = self.playbook_engine.list_available_routes()
        
        print("\n╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                        📚 AVAILABLE PLAYBOOK ROUTES                          ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝\n")
        
        for route in routes:
            print(f"🎯 {route['name'].upper()}")
            print(f"   {route['description']}")
            print(f"   Examples: {', '.join(route['examples'])}")
            print()
    
    def health_check(self) -> bool:
        """Quick health check - returns True if system is operational"""
        try:
            context = self.context_loader.load()
            
            # Check critical components
            git_ok = context.get('git', {}).get('status') == 'available'
            env_ok = context.get('environment', {}).get('status') in ['ready', 'needs_setup']
            
            if not git_ok:
                print("⚠️ Git not available", file=sys.stderr)
            if not env_ok:
                print("⚠️ Environment issues detected", file=sys.stderr)
            
            return git_ok and env_ok
        except Exception as e:
            print(f"❌ Health check failed: {e}", file=sys.stderr)
            return False

import os
import sys
import argparse

# Force UTF-8 stdout encoding for Windows console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from resume_screener.agent import ResumeScreeningAgent

console = Console(force_terminal=True, legacy_windows=False)

def main():
    parser = argparse.ArgumentParser(
        description="Rooman 24-Hour AI Challenge: AI Resume Screening Agent"
    )
    parser.add_argument(
        "--jd",
        type=str,
        default=os.path.join("data", "sample_jds", "senior_ai_engineer.txt"),
        help="Path to Job Description file or direct text"
    )
    parser.add_argument(
        "--resumes",
        type=str,
        default=os.path.join("data", "sample_resumes"),
        help="Directory containing candidate resume files (.pdf, .docx, .txt)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs",
        help="Output directory for ranked CSV and JSON reports"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Optional OpenAI or Groq API Key for LLM semantic evaluation"
    )

    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]ROOMAN AI CHALLENGE - AI RESUME SCREENING AGENT[/bold cyan]\n"
        "[dim]Automated Candidate Resume Parsing, Hybrid NLP/LLM Scoring & Shortlisting[/dim]",
        border_style="cyan"
    ))

    # Initialize Agent
    agent = ResumeScreeningAgent(api_key=args.api_key)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task(description="Parsing Job Description & Candidate Resumes...", total=None)
        results = agent.screen_resumes_folder(args.resumes, args.jd, output_dir=args.output)

    total = results["total_candidates"]
    avg_score = results["average_score"]
    top = results["top_candidate"]

    console.print(f"\n[bold green]Screening Complete![/bold green] Processed [bold]{total}[/bold] candidates. Average Score: [bold yellow]{avg_score}/100[/bold yellow]\n")

    # Render Leaderboard Table
    table = Table(title="Candidate Shortlist Leaderboard", header_style="bold magenta", border_style="dim")
    table.add_column("Rank", justify="center", style="bold yellow", width=6)
    table.add_column("Candidate Name", style="bold white", width=22)
    table.add_column("Final Score", justify="center", style="bold green", width=12)
    table.add_column("Recommendation Tier", style="cyan", width=32)
    table.add_column("Format", justify="center", style="dim", width=8)
    table.add_column("Matched Skills", style="blue", width=30)

    for c in results["ranked_candidates"]:
        matched_str = ", ".join(c["matched_skills"][:4])
        if len(c["matched_skills"]) > 4:
            matched_str += f" (+{len(c['matched_skills'])-4} more)"

        score_style = "bold green" if c["final_score"] >= 80 else "bold yellow" if c["final_score"] >= 65 else "bold red"
        table.add_row(
            f"#{c['rank']}",
            c["candidate_name"],
            f"[{score_style}]{c['final_score']}/100[/{score_style}]",
            c["recommendation"],
            c["format"],
            matched_str or "None"
        )

    console.print(table)

    # Top Candidate Highlight
    if top:
        console.print("\n[bold gold1]TOP CANDIDATE HIGHLIGHT[/bold gold1]")
        top_panel = (
            f"[bold white]Name:[/bold white] {top['candidate_name']} (Rank #{top['rank']})\n"
            f"[bold white]Final Score:[/bold white] [bold green]{top['final_score']}/100[/bold green]\n"
            f"[bold white]Experience:[/bold white] {top['experience_years']} Years | [bold white]Education:[/bold white] {', '.join(top['education'])}\n"
            f"[bold white]Reasoning:[/bold white] [italic]{top['reasoning']}[/italic]\n"
            f"[bold white]Key Strengths:[/bold white] {', '.join(top['strengths'])}\n"
            f"[bold white]Missing Skills:[/bold white] {', '.join(top['missing_skills']) or 'None'}"
        )
        console.print(Panel(top_panel, title="Candidate #1 Details", border_style="gold1"))

    # Export paths
    console.print("\n[bold cyan]Generated Deliverables:[/bold cyan]")
    console.print(f"  * JSON Report: [underline]{results['outputs']['json']}[/underline]")
    console.print(f"  * CSV Report:  [underline]{results['outputs']['csv']}[/underline]\n")

if __name__ == "__main__":
    main()

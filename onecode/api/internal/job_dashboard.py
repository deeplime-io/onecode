import os

import httpx
from dateutil.parser import isoparse
from rich.panel import Panel
from rich.table import Table
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Footer, Header, Static

from ...base.enums import ConfigOption, Env
from ...base.project import Project

_STATUS_ORDER = [
    "init", "provisioning", "running", "post-processing", "failed", "success"
]

_STATUS_KEYS = {
    "1": "init",
    "2": "provisioning",
    "3": "running",
    "4": "post-processing",
    "5": "failed",
    "6": "success"
}

_STATUS_COLORS = {
    "init": "yellow",
    "provisioning": "yellow",
    "running": "cyan",
    "post-processing": "yellow",
    "failed": "red",
    "success": "green"
}


class _Countdown(Static):
    def update_countdown(self, seconds: int):
        self.update(f"[bold white]Refresh in: {seconds}s[/bold white]")


class _JobDashboard(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "filter_all", "All Statuses"),
        ("r", "filter_running", "Only Running"),
        ("1", "toggle_status_1", "Toggle init"),
        ("2", "toggle_status_2", "Toggle provisioning"),
        ("3", "toggle_status_3", "Toggle running"),
        ("4", "toggle_status_4", "Toggle post-processing"),
        ("5", "toggle_status_5", "Toggle failed"),
        ("6", "toggle_status_6", "Toggle success"),
    ]

    job_data = reactive([])
    visible_statuses = reactive(set(_STATUS_ORDER))
    refresh_in = reactive(3)

    # Widgets
    countdown_widget: _Countdown
    dashboard_container: Container

    # Timers
    countdown_timer: Timer
    refresh_timer: Timer

    def __init__(
        self,
        slug: str,
        max_jobs: int,
        refresh: int,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._slug = slug
        self._max_jobs = max_jobs
        self._refresh = refresh
        self.theme = "nord"

    def compose(self) -> ComposeResult:
        self.countdown_widget = _Countdown()
        self.dashboard_container = VerticalScroll(self.countdown_widget, id="dashboard")
        # self.dashboard_container.styles.padding = 1
        # self.dashboard_container.styles.scrollbar_gutter = "stable"
        # self.dashboard_container.styles.overflow_y = "scroll"

        yield Header()
        yield self.dashboard_container
        yield Footer()

    async def on_mount(self):
        self.countdown_timer = self.set_interval(1, self.update_countdown)
        self.refresh_timer = self.set_interval(self._refresh, self.fetch_jobs)
        await self.fetch_jobs()

    def update_countdown(self):
        self.refresh_in = max(0, self.refresh_in - 1)
        self.countdown_widget.update_countdown(self.refresh_in)

    async def fetch_jobs(self):
        self.refresh_in = self._refresh
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{Project().get_config(ConfigOption.API_URL)}/apps/exec/jobs/{self._slug}"
                    f"?max_jobs={self._max_jobs}",
                    headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
                )
                response.raise_for_status()
                self.job_data = response.json().get("jobs", [])
        except Exception as e:
            self.job_data = [{
                "id": "ERROR",
                "status": "failed",
                "type": "N/A",
                "createdAt": "",
                "finishedAt": str(e)
            }]
        self.update_table()

    def update_table(self):
        # Remove old table panel, but keep countdown
        for child in self.dashboard_container.children[1:]:
            child.remove()

        table = Table(title="Job Status", expand=True)
        table.add_column("ID", style="dim")
        table.add_column("Status", style="bold")
        table.add_column("Type")
        table.add_column("Created At")
        table.add_column("Finished At")

        for job in self.job_data:
            if job["status"] not in self.visible_statuses:
                continue

            status = job["status"]
            color = _STATUS_COLORS.get(status, "white")

            table.add_row(
                str(job["id"]),
                f"[{color}]{status}[/]",
                job["type"],
                self.format_datetime(job["createdAt"]),
                self.format_datetime(job.get("finishedAt", ""))
            )

        self.dashboard_container.mount(Static(Panel(table)))

    def format_datetime(self, dt_str: str):
        if not dt_str:
            return ""
        try:
            dt = isoparse(dt_str)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return dt_str

    # Filter handlers
    def action_filter_all(self):
        self.visible_statuses = set(_STATUS_ORDER)
        self.update_table()

    def action_filter_running(self):
        self.visible_statuses = {"init", "provisioning", "running", "post-processing"}
        self.update_table()

    def toggle_status(self, key: str):
        status = _STATUS_KEYS[key]
        if status in self.visible_statuses:
            self.visible_statuses.remove(status)
        else:
            self.visible_statuses.add(status)
        self.update_table()

    def action_toggle_status_1(self): self.toggle_status("1")
    def action_toggle_status_2(self): self.toggle_status("2")
    def action_toggle_status_3(self): self.toggle_status("3")
    def action_toggle_status_4(self): self.toggle_status("4")
    def action_toggle_status_5(self): self.toggle_status("5")
    def action_toggle_status_6(self): self.toggle_status("6")

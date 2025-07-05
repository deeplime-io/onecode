import asyncio
import os

import httpx
import pyperclip
from dateutil.parser import isoparse
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import DataTable, Footer, Header, Static

from ....base.enums import ConfigOption, Env
from ....base.project import Project
from .logs import _COLORMAPS
from .utils import get_datetime

_STATUS_ORDER = [
    "init", "provisioning", "running", "post-processing", "failed", "success"
]


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


class _LogScreen(Screen):
    CSS = """
    _LogScreen {
        padding: 1;
        height: 100%;
        scrollbar-gutter: stable;
        overflow-y: auto;
    }
    """

    BINDINGS = [
        ("q", "app.pop_screen", "Close"),
        ("l", "app.pop_screen", "Close"),
        ("escape", "app.pop_screen", "Close")
    ]

    def __init__(
        self,
        job_id: str,
        initial_logs: list[dict],
        status: str
    ):
        super().__init__()
        self.job_id = job_id
        self.logs = initial_logs
        self.status = status
        self.last_ts = max((entry["timestamp"] for entry in initial_logs), default=0)
        self.container = VerticalScroll(id="log-scroll")

    def compose(self):
        self.container = VerticalScroll(id="log-scroll")
        yield self.container

    async def on_mount(self):
        for entry in self.logs:
            await self.container.mount(self._render_log(entry))

        self.run_worker(self._poll_logs(), exclusive=True)

    async def _poll_logs(self):
        finished = self.status in ['failed', 'success']
        if finished:
            self.notify(f"Status: {self.status}", timeout=3)

        while not finished:
            try:
                self.notify(f"Status: {self.status} => fetching...", timeout=1.5)
                async with httpx.AsyncClient() as client:
                    status_res = await client.get(
                        f'{Project().get_config(ConfigOption.API_URL)}'
                        f'/apps/exec/status/{self.job_id}',
                        headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
                    )
                    if not status_res.is_success:
                        raise Exception(
                            f"{status_res.status_code}: "
                            f"{status_res.json().get('error', 'Unknown error')}"
                        )
                    self.status = status_res.json().get("job_status")

                    logs_res = await client.get(
                        f'{Project().get_config(ConfigOption.API_URL)}'
                        f'/apps/exec/logs/{self.job_id}',
                        params={
                            "after": self.last_ts + 1000
                        },
                        headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
                    )
                    if not logs_res.is_success:
                        raise Exception(
                            f"{logs_res.status_code}: "
                            f"{logs_res.json().get('error', 'Unknown error')}"
                        )

                    new_logs = logs_res.json().get("logs", [])
                    for entry in new_logs:
                        await self.container.mount(self._render_log(entry))
                        self.last_ts = max(self.last_ts, entry["timestamp"])
                    await asyncio.sleep(3)
            except Exception as e:
                await self.container.mount(Static(f"[red]Log error: {e}[/]", markup=True))
                await asyncio.sleep(5)

    def _render_log(self, entry: dict) -> Static:
        ts = get_datetime(entry["timestamp"])
        msg = entry["message"]
        color = entry.get("color", "white")
        if color in _COLORMAPS:
            color = _COLORMAPS[color]
        return Static(f"[{color}]{ts} - {msg}[/]", markup=True)


class _JobDashboard(App):
    TITLE = "Job Dashboard"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "filter_all", "All Statuses"),
        ("r", "filter_running", "Only running"),
        ("f", "filter_failed", "Only failed"),
        ("s", "filter_success", "Only success"),
        ("c", "copy_job", "Copy selected job"),
        ("l", "get_job_logs", "Display job log"),
    ]

    job_data = reactive([])
    visible_statuses = reactive(set(_STATUS_ORDER))
    refresh_in = reactive(3)
    row_index_to_job: dict[int, dict]

    # Widgets
    countdown_widget: _Countdown
    dashboard_container: Container
    table: DataTable

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
        self.table = DataTable(zebra_stripes=True)
        self.table.cursor_type = "row"

        self.dashboard_container = Container(
            self.countdown_widget,
            self.table,
            id="dashboard"
        )

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
                    f"{Project().get_config(ConfigOption.API_URL)}/apps/exec/jobs/{self._slug}",
                    params={
                        "max_jobs": self._max_jobs
                    },
                    headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
                )
                if not response.is_success:
                    raise Exception(
                        f"{response.status_code}: "
                        f"{response.json().get('error', 'Unknown error')}"
                    )

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
        self.table.clear(columns=True)
        self.table.add_columns("ID", "Status", "Type", "Created At", "Finished At")

        self.row_index_to_job = []

        for job in self.job_data:
            if job["status"] not in self.visible_statuses:
                continue

            row = (
                str(job["id"]),
                Text(job["status"], style=_STATUS_COLORS.get(job["status"], "white")),
                job["type"],
                self.format_datetime(job["createdAt"]),
                self.format_datetime(job.get("finishedAt", ""))
            )
            self.table.add_row(*row)
            self.row_index_to_job.append(job)

        self.table.focus()
        if len(self.row_index_to_job) > 0:
            self.table.cursor_coordinate = (0, 0)

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

    def action_filter_failed(self):
        self.visible_statuses = {"failed"}
        self.update_table()

    def action_filter_success(self):
        self.visible_statuses = {"success"}
        self.update_table()

    def action_copy_job(self):
        selected = self.table.cursor_row
        if selected is not None and selected < len(self.row_index_to_job):
            job = self.row_index_to_job[selected]
            try:
                pyperclip.copy(str(job['id']))
                self.notify("Job ID copied to clipboard", timeout=3)
            except Exception as e:
                self.notify(f"Failed to copy to clipboard: {str(e)}", timeout=5, severity="error")

    async def action_get_job_logs(self):
        selected = self.table.cursor_row
        if selected is not None and selected < len(self.row_index_to_job):
            job = self.row_index_to_job[selected]
            job_id = job["id"]
            self.notify(f"Logs for job: {job_id}", timeout=3)

            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    logs_res = await client.get(
                        f'{Project().get_config(ConfigOption.API_URL)}/apps/exec/logs/{job_id}',
                        headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
                    )
                    if not logs_res.is_success:
                        raise Exception(
                            f"{logs_res.status_code}: "
                            f"{logs_res.json().get('error', 'Unknown error')}"
                        )

                    logs = logs_res.json().get("logs", [])
                    await self.app.push_screen(_LogScreen(job_id, logs, job["status"]))

            except Exception as e:
                self.notify(f"Error: {e}", severity="error", timeout=5)

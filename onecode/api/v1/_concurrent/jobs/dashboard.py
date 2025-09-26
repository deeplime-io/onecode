import asyncio
from datetime import timezone

import httpx
import pyperclip
from dateutil.parser import isoparse
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Header, Static

from ....utils import (
    _COLORMAPS,
    JOB_STATUS,
    api_timeout,
    api_token,
    api_url,
    get_datetime
)
from .logs import async_logs

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
        if self.status in ['failed', 'success']:
            self.notify(f"Status: {self.status}", timeout=3)

        while self.status not in ['failed', 'success']:
            try:
                self.notify(f"Status: {self.status} => fetching...", timeout=1.5)
                self.status, logs = await async_logs(
                    self.job_id,
                    after=self.last_ts + 1,
                    wait=3
                )
                for entry in logs:
                    await self.container.mount(self._render_log(entry))
                    self.last_ts = max(self.last_ts, entry["timestamp"])
            except Exception as e:
                await self.container.mount(Static(f"[red]Log error: {str(e)}[/]", markup=True))
                await asyncio.sleep(5)

    def _render_log(self, entry: dict) -> Static:
        ts = get_datetime(entry["timestamp"])
        msg = entry["message"]
        color = entry.get("color", "white")
        if color in _COLORMAPS:
            color = _COLORMAPS[color]
        return Static(f"[{color}]{ts} - {msg}[/]", markup=True)


class _LoadingModal(Widget):
    DEFAULT_CSS = """
    _LoadingModal {
        layer: overlay;
        background: rgba(0, 0, 0, 0.6); /* dark translucent */
        height: 100%;
        width: 100%;
        align: center middle;
    }

    _LoadingModal > .modal-box {
        background: $panel;
        border: round $accent;
        padding: 2 4;
        content-align: center middle;
    }
    """

    def compose(self):
        yield Container(
            Static("⏳ [bold]Loading logs...[/]", markup=True),
            classes="modal-box"
        )


class JobDashboard(App):
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
    visible_statuses = reactive(set(JOB_STATUS))
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
        self.table.add_columns("ID", "Status", "Type", "Created At", "Finished At")

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
            async with httpx.AsyncClient(timeout=api_timeout()) as client:
                response = await client.get(
                    f"{api_url()}/apps/exec/jobs/{self._slug}",
                    params={
                        "max_jobs": self._max_jobs
                    },
                    headers=api_token()
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
        # record selection
        cursor_row = self.table.cursor_row
        selected_job_id = None
        if cursor_row is not None and len(self.table.rows) > 0:
            selected = self.table.get_row_at(cursor_row)
            if selected:
                selected_job_id = selected[0]

        self.table.clear(columns=False)
        self.row_index_to_job = []

        for job in self.job_data:
            if job["status"] not in self.visible_statuses:
                continue

            row = (
                str(job["id"]),
                Text(job["status"], style=_STATUS_COLORS.get(job["status"], "white")),
                job["type"],
                self.format_datetime(job.get("createdAt", "")),
                self.format_datetime(job.get("finishedAt", ""))
            )
            self.table.add_row(*row)
            self.row_index_to_job.append(job)

        self.table.focus()

        # Restore selection
        table_size = len(self.table.rows)
        if selected_job_id is not None and table_size > 0:
            for i in range(table_size):
                if self.table.get_row_at(i)[0] == selected_job_id:
                    self.table.move_cursor(row=i)
                    break

    def format_datetime(self, dt_str: str):
        if not dt_str:
            return ""
        try:
            # Dates are known to be UTC in DB but TZ is not stored.
            dt = isoparse(dt_str).replace(tzinfo=timezone.utc).astimezone()
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return dt_str

    # Filter handlers
    def action_filter_all(self):
        self.visible_statuses = set(JOB_STATUS)
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
            self.loading_modal = _LoadingModal()
            await self.mount(self.loading_modal)

            job = self.row_index_to_job[selected]
            job_id = job["id"]
            self.notify(f"Logs for job: {job_id}", timeout=3)

            try:
                status, logs = await async_logs(job_id)
                await self.app.push_screen(_LogScreen(job_id, logs, status))

            except Exception as e:
                self.notify(f"Error: {str(e)}", severity="error", timeout=5)

            finally:
                await self.loading_modal.remove()

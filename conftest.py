from sys import maxsize
import os
import pyautogui
import pytest
from pytest_html import extras
from pathlib import Path
import shutil
import time
from datetime import datetime
from typing import Optional, Callable
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
    expect,
    Locator
)

# =========================
# Paths & Globals
# =========================
global_browser: Optional[Browser] = None
global_context: Optional[BrowserContext] = None
global_pages: list[Page] = []

# =========================
# Config
# =========================
ARTIFACTS_DIR = Path("artifacts")
print(f"Artifacts path: {ARTIFACTS_DIR}")
VIDEOS_DIR = ARTIFACTS_DIR / "videos"
TRACES_DIR = ARTIFACTS_DIR / "traces"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
screen_width, screen_height = pyautogui.size()

# =========================
# Auto-highlighter settings
# =========================
def _env_truthy(val: str | None) -> bool:
    if val is None:
        return False
    return val.strip().lower() in {"1", "true", "yes", "on"}

HIGHLIGHT_ENABLED = _env_truthy(os.getenv("HIGHLIGHT_ELEMENTS", "1"))
try:
    HIGHLIGHT_DURATION_MS = int(os.getenv("HIGHLIGHT_DURATION_MS", "800"))
except Exception:
    HIGHLIGHT_DURATION_MS = 800

# Colors used per action
ACTION_COLORS = {
    "click": "#ff6b6b",
    "dblclick": "#ff6b6b",
    "type": "#4dabf7",
    "fill": "#4dabf7",
    "press": "#ffd43b",
    "hover": "#51cf66",
    "check": "#51cf66",
    "uncheck": "#ff922b",
    "select_option": "#845ef7",
    "focus": "#66d9ef",
    "blur": "#c3fae8",
}

# =========================
# Pytest HTML report setup
# =========================
def pytest_configure(config):
    ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)
    VIDEOS_DIR.mkdir(exist_ok=True, parents=True)
    TRACES_DIR.mkdir(exist_ok=True, parents=True)
    SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)

    config.artifacts_dir = ARTIFACTS_DIR
    config.videos_dir = VIDEOS_DIR
    config.traces_dir = TRACES_DIR
    config.screenshots_dir = SCREENSHOTS_DIR

    # Custom metadata for HTML report
    report_title = getattr(config.option, "report_title", "Test Report")
    config._metadata = getattr(config, "_metadata", {})
    config._metadata["Report Title"] = report_title

    # Show browser name in HTML metadata
    browser_env = os.getenv("BROWSER", "chrome").lower()
    config._metadata["Browser"] = browser_env.capitalize()

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Auto-open the HTML report after run completes (Windows only for simplicity).
    """
    htmlpath = getattr(session.config, "htmlpath", None)
    if htmlpath and Path(htmlpath).exists():
        try:
            if os.name == "nt":
                os.startfile(str(htmlpath))
            elif sys.platform == "darwin":
                os.system(f'open "{htmlpath}"')
            else:
                os.system(f'xdg-open "{htmlpath}" >/dev/null 2>&1 &')
        except Exception:
            pass

# =========================
# Playwright fixtures
# =========================
@pytest.fixture(scope="session")
def playwright() -> Playwright: # type: ignore
    with sync_playwright() as p:
        yield p # type: ignore

@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Browser: # type: ignore
    """
    Browser fixture supporting Chrome or Firefox selection.
    Choose via CLI (--browser=firefox) or env var (BROWSER=firefox)
    """
    global global_browser

    # Detect from CLI or environment
    browser_choice = "chrome"
    for arg in os.sys.argv: # type: ignore
        if arg.startswith("--browser="):
            browser_choice = arg.split("=")[1].strip().lower()
            break
    browser_choice = os.getenv("BROWSER", browser_choice).lower()

    print(f"\n🚀 Launching browser: {browser_choice}")

    if global_browser is None:
        if browser_choice == "firefox":
            global_browser = playwright.firefox.launch(
                headless=False,
                slow_mo=200,
                args=["--width=1920", "--height=1080"],
            )
        else:
            global_browser = playwright.chromium.launch(
                headless=False,
                slow_mo=200,
                args=[
                    "--start-maximized",
                    "--window-position=0,0",
                    "--high-dpi-support=1",
                    "--force-device-scale-factor=1",
                    "--disable-http2",
                    "--disable-features=NetworkService",
                    "--lang=en-US",
                    "--ignore-certificate-errors",
                ],
            )

    yield global_browser # type: ignore
    if global_browser:
        global_browser.close()
        global_browser = None

@pytest.fixture(scope="session")
def context(browser: Browser) -> BrowserContext: # type: ignore
    global global_context, global_pages
    if global_context is None:
        global_context = browser.new_context(
            viewport={"width": screen_width, "height": screen_height},
            device_scale_factor=1,
            record_video_dir=VIDEOS_DIR,
            record_video_size={"width": screen_width, "height": screen_height},
            locale="en-US",
        )
        page = global_context.new_page()
        page.set_viewport_size({"width": screen_width, "height": screen_height})
        try:
            page.evaluate("window.moveTo(0,0); window.resizeTo(screen.width, screen.height);")
        except Exception:
            pass
        global_pages = [page]
    yield global_context # type: ignore
    if global_context:
        try:
            global_context.close()
        except Exception:
            pass
        global_context = None

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    global global_pages
    if not global_pages:
        global_pages = [context.new_page()]
    page = global_pages[-1]
    page.bring_to_front()
    return page

@pytest.fixture
def open_new_page(context: BrowserContext):
    def _open(action: Callable[[Page], None]) -> Page:
        global global_pages
        with context.expect_page() as new_page_info:
            action(global_pages[-1])
        page = new_page_info.value
        global_pages.append(page)
        page.bring_to_front()
        return page
    return _open

@pytest.fixture
def screenshot(request):
    def _capture(driver, name: str = "screenshot"):
        screenshots_dir = request.config.screenshots_dir
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{request.node.name}_{name}_{timestamp}.png"
        filepath = screenshots_dir / filename
        driver.save_screenshot(str(filepath))
        extra = getattr(request.node, "extra", [])
        extra.append(extras.image(str(filepath)))
        request.node.extra = extra
        return filepath
    return _capture

# =========================
# Trace/video handling
# =========================
@pytest.fixture(autouse=True)
def _trace_video_recording(request, context: BrowserContext):
    test_name = request.node.name
    trace_path = TRACES_DIR / f"{test_name}_{int(time.time())}.zip"

    try:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
    except Exception:
        pass

    yield

    try:
        context.tracing.stop(path=str(trace_path))
    except Exception:
        pass

# =========================
# Auto-highlighter helpers
# =========================
def _flash_selector(page: Page, selector: str, action: str, duration_ms: int = HIGHLIGHT_DURATION_MS) -> None:
    try:
        color = ACTION_COLORS.get(action, "red")
        page.eval_on_selector(
            selector,
            f"""(el) => {{
                const prev = el.style.outline;
                el.style.outline = '3px solid {color}';
                setTimeout(() => {{ el.style.outline = prev; }}, {duration_ms});
            }}"""
        )
    except Exception:
        pass

def _flash_locator(locator: Locator, action: str, duration_ms: int = HIGHLIGHT_DURATION_MS) -> None:
    try:
        color = ACTION_COLORS.get(action, "red")
        locator.evaluate(
            f"""(el) => {{
                const prev = el.style.outline;
                el.style.outline = '3px solid {color}';
                setTimeout(() => {{ el.style.outline = prev; }}, {duration_ms});
            }}"""
        )
    except Exception:
        pass

def highlight_selector(page: Page, selector: str, action: str) -> None:
    _flash_selector(page, selector, action)

def highlight_locator(locator: Locator, action: str) -> None:
    _flash_locator(locator, action)

# =========================
# Scroll-to-element implementation
# =========================
from typing import Union

def _is_in_viewport(locator: Locator) -> bool:
    try:
        return bool(locator.evaluate("""(el) => {
            const r = el.getBoundingClientRect();
            const vh = window.innerHeight || document.documentElement.clientHeight;
            const vw = window.innerWidth  || document.documentElement.clientWidth;
            return r.top >= 0 && r.left >= 0 && r.bottom <= vh && r.right <= vw;
        }"""))
    except Exception:
        return False

def scroll_locator(
    locator: Locator,
    align: str = "center",
    padding: int = 80,
    timeout: int = 5000,
    attempts: int = 3,
) -> None:
    locator.wait_for(state="attached", timeout=timeout)
    for _ in range(attempts):
        try:
            if _is_in_viewport(locator):
                return
            locator.evaluate(f"""(el) => {{
                el.scrollIntoView({{ behavior: 'instant', block: '{align}', inline: 'nearest' }});
            }}""")
            locator.evaluate(f"""(el) => {{
                const r = el.getBoundingClientRect();
                const desiredTop = Math.max(r.top - {padding}, 0);
                window.scrollBy(0, desiredTop - r.top);
            }}""")
            if _is_in_viewport(locator):
                return
        except Exception:
            pass
    try:
        locator.scroll_into_view_if_needed(timeout=timeout)
    except Exception:
        pass

def scroll_selector(
    page: Page,
    selector: str,
    align: str = "center",
    padding: int = 80,
    timeout: int = 5000,
    attempts: int = 3,
) -> None:
    page.wait_for_selector(selector, state="attached", timeout=timeout)
    scroll_locator(page.locator(selector), align=align, padding=padding, timeout=timeout, attempts=attempts)

def _install_auto_highlighter():
    if getattr(Page, "_auto_highlight_installed", False):
        return
    page_methods = list(ACTION_COLORS.keys())
    locator_methods = list(ACTION_COLORS.keys())
    for method_name in page_methods:
        if not hasattr(Page, method_name):
            continue
        original = getattr(Page, method_name)
        def make_wrapper(_original, _method_name):
            def wrapper(self: Page, selector: str, *args, **kwargs):
                if isinstance(selector, str):
                    try:
                        scroll_selector(self, selector, align="center", padding=100, timeout=5000)
                    except Exception:
                        pass
                    if HIGHLIGHT_ENABLED:
                        try:
                            highlight_selector(self, selector, _method_name)
                        except Exception:
                            pass
                return _original(self, selector, *args, **kwargs)
            return wrapper
        setattr(Page, method_name, make_wrapper(original, method_name))

    for method_name in locator_methods:
        if not hasattr(Locator, method_name):
            continue
        original = getattr(Locator, method_name)
        def make_loc_wrapper(_original, _method_name):
            def wrapper(self: Locator, *args, **kwargs):
                try:
                    scroll_locator(self, align="center", padding=100, timeout=5000)
                except Exception:
                    pass
                if HIGHLIGHT_ENABLED:
                    try:
                        highlight_locator(self, _method_name)
                    except Exception:
                        pass
                return _original(self, *args, **kwargs)
            return wrapper
        setattr(Locator, method_name, make_loc_wrapper(original, method_name))
    setattr(Page, "_auto_highlight_installed", True)

try:
    _install_auto_highlighter()
except Exception:
    pass
# =========================
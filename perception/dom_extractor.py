from playwright.sync_api import Page

def extract_dom(page: Page) -> str:
    """
    Injects JavaScript into the page to extract interactive elements,
    assigns them IDs, draws visual bounding boxes with labels,
    and returns a clean text summary for the LLM.
    """
    js_code = """
    () => {
        let elements = document.querySelectorAll('button, a, input, textarea, select, [role="button"]');
        let items = [];
        let id_counter = 1;
        
        elements.forEach(el => {
            const style = window.getComputedStyle(el);
            // Basic visibility check
            if (el.offsetWidth > 0 && el.offsetHeight > 0 && style.visibility !== 'hidden' && style.display !== 'none' && style.opacity > 0) {
                let id = id_counter++;
                el.setAttribute('agent-id', id);
                
                // Visual Highlight: Draw outline (avoids layout shift compared to border)
                el.style.outline = '2px solid red';
                el.style.outlineOffset = '-2px';
                
                // Visual Highlight: Create ID label
                let label = document.createElement('div');
                label.textContent = id;
                label.style.position = 'absolute';
                label.style.background = 'red';
                label.style.color = 'white';
                label.style.fontSize = '12px';
                label.style.fontWeight = 'bold';
                label.style.padding = '1px 3px';
                label.style.zIndex = '999999';
                label.style.pointerEvents = 'none'; // Don't block clicks on the actual element
                label.style.borderRadius = '3px';
                
                let rect = el.getBoundingClientRect();
                label.style.top = Math.max(0, (rect.top + window.scrollY - 15)) + 'px'; // Place slightly above
                label.style.left = (rect.left + window.scrollX) + 'px';
                document.body.appendChild(label);
                
                // Extract text context for the LLM
                let text = el.innerText || el.placeholder || el.name || el.title || el.ariaLabel || '';
                text = text.trim();
                
                // CRITICAL: If the field has a value (text was typed into it), show it to the LLM
                // Otherwise, the LLM won't know it already typed the username and will get stuck in a loop!
                if ((el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') && el.value) {
                    text += ` (current value: '${el.value}')`;
                }
                
                items.push(`[${id}] <${el.tagName.toLowerCase()}> "${text}"`);
            }
        });
        
        let summary = `PAGE TITLE: ${document.title}\\nPAGE URL: ${window.location.href}\\n\\nInteractive Elements:\\n`;
        return summary + items.join('\\n');
    }
    """
    try:
        return page.evaluate(js_code)
    except Exception:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=3000)
            return page.evaluate(js_code)
        except Exception as e:
            print(f"Warning: DOM extraction during navigation retry failed: {e}")
            return ""

def check_for_captcha(page: Page) -> bool:
    """
    Checks if a CAPTCHA or anti-bot security challenge (Cloudflare, reCAPTCHA, hCaptcha)
    is currently visible or active on the page.
    """
    # 1. Check Page Title for Cloudflare / Security challenge indicators
    try:
        title = page.title().lower()
        title_keywords = ["just a moment", "attention required", "cloudflare", "security check", "robot or human"]
        for kw in title_keywords:
            if kw in title:
                return True
    except Exception:
        pass

    # 2. Check DOM selectors for known CAPTCHA elements & Cloudflare challenge containers
    captcha_selectors = [
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "iframe[src*='challenges.cloudflare.com']",
        ".g-recaptcha",
        ".h-captcha",
        "#captcha",
        "#challenge-stage",
        "#challenge-form",
        ".cf-turnstile",
        "[id*='cf-challenge']"
    ]
    for selector in captcha_selectors:
        try:
            loc = page.locator(selector).first
            if loc.count() > 0:
                box = loc.bounding_box()
                if loc.is_visible() or (box and box["width"] > 0 and box["height"] > 0):
                    return True
        except Exception:
            pass
            
    # 3. Check visible page text for Cloudflare / Bot verification phrases
    try:
        body_text = page.locator("body").inner_text(timeout=1000).lower()
        keywords = [
            "verify you are human",
            "security check",
            "solve the captcha",
            "just a moment...",
            "checking if the site connection is secure",
            "enable javascript and cookies to continue"
        ]
        for keyword in keywords:
            if keyword in body_text:
                return True
    except Exception:
        pass
        
    return False

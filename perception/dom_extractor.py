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
        
        return items.join('\\n');
    }
    """
    return page.evaluate(js_code)

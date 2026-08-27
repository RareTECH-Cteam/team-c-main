(() => {
    const resultView = document.querySelector(
        "[data-conversion-result-view]"
    );

    if (!resultView) {
        return;
    }

    let statusTimer;

    function announce(message) {
        const status = resultView.querySelector(
            "[data-copy-status]"
        );

        if (!status) {
            return;
        }

        window.clearTimeout(statusTimer);

        status.textContent = message;
        status.hidden = false;

        statusTimer = window.setTimeout(() => {
            status.hidden = true;
        }, 3000);
    }

    resultView.addEventListener("click", async (event) => {
        if (!(event.target instanceof Element)) {
            return;
        }

        const feedbackButton = event.target.closest(
            "[data-feedback]"
        );

        if (feedbackButton) {
            resultView.dispatchEvent(
                new CustomEvent("conversion:feedback", {
                    bubbles: true,
                    detail: {
                        adjustment: feedbackButton.dataset.feedback,
                    },
                })
            );

            return;
        }

        const copyButton = event.target.closest(
            "[data-copy-button]"
        );

        if (copyButton) {
            const targetId = copyButton.dataset.copyTarget;
            const target = document.getElementById(targetId);

            try {
                if (!target || !navigator.clipboard?.writeText) {
                    throw new Error("Clipboard API unavailable");
                }

                await navigator.clipboard.writeText(
                    target.textContent.trim()
                );

                announce("コピーしました");
            } catch {
                announce("コピーできませんでした。文章を選択してコピーしてください");
            }

            return;
        }

        const reasonButton = event.target.closest(
            "[data-reason-toggle]"
        );

        if (reasonButton) {
            const reasonId = reasonButton.getAttribute(
                "aria-controls"
            );
            const reason = document.getElementById(reasonId);

            if (!reason) {
                return;
            }

            const willOpen = reasonButton.getAttribute("aria-expanded") !== "true";

            reasonButton.setAttribute(
                "aria-expanded",
                String(willOpen)
            );

            reason.hidden = !willOpen;
            reasonButton.hidden = willOpen;

            if (willOpen) {
                reason.querySelector("[data-reason-close]")?.focus();
            }
        }

        if (event.target.closest("[data-reason-close]")) {
            const reasonButton = resultView.querySelector("[data-reason-toggle]");

            const reason = resultView.querySelector("#conversion-reason");

            if (!reasonButton || !reason) {
                return;
            }

            reason.hidden = true;
            reasonButton.hidden = false;
            reasonButton.setAttribute("aria-expanded", "false");
            reasonButton.focus();
        }
    });
})();
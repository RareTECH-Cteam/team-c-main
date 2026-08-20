(() => {
    const dialog = document.querySelector("#login-required-dialog");
    const trigger = document.querySelectorAll("[data-login-modal-trigger]");
    const closeButton = dialog?.querySelector("[data-modal-close]");

    if (!dialog || typeof dialog.showModal !== "function"
    ) {
        return;
    }

    let opener = null;

    function openDialog(trigger) {
        if (dialog.open) {
            return;
        }

        opener = trigger;

        document.documentElement.classList.add(
            "is-login-dialog-open"
        );

        dialog.showModal();
        closeButton?.focus();
    }

    function closeDialog() {
        if (dialog.open) {
            dialog.close();
        }
    }

    trigger.forEach((trigger) => {
        trigger.addEventListener("click", () => {
            openDialog(trigger);
        });
    });

    closeButton?.addEventListener("click", closeDialog);

    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) {
            closeDialog();
        }
    });

    dialog.addEventListener("cancel", (event) => {
        event.preventDefault();
        closeDialog();
    });

    dialog.addEventListener("close", () => {
        document.documentElement.classList.remove(
            "is-login-dialog-open"
        );

        const focusTarget = opener;
        opener = null;

        if (focusTarget?.isConnected) {
            focusTarget.focus();
        }
    });

    // APIがAUTH__REQUIREDを返した場合でもモーダルを表示
    window.addEventListener(
        "conversion:auth-required",
        () => {
            const activeElement = document.activeElement instanceof HTMLElement
                ? document.activeElement : trigger[0];

            openDialog(activeElement);
        }
    );
})();
(() => {
    const form = document.querySelector("[data-conversion-form]");

    const switcher = document.querySelector("[data-conversion-mode-switch]");

    if (!form || !switcher) {
        return;
    }

    const modeControls = Array.from(
        switcher.querySelectorAll("[data-conversion-mode-control]")
    );

    const panels = Array.from(
        form.querySelectorAll("[data-conversion-mode-panel]")
    );

    const setPanelControlsDisabled = (panel, disabled) => {
        panel.querySelectorAll("fieldset").forEach((fieldset) => {
            fieldset.disabled = disabled;
        });
    };

    const activateMode = (mode) => {
        panels.forEach((panel) => {
            const isActive = panel.dataset.conversionModePanel === mode;
            panel.hidden = !isActive;
            setPanelControlsDisabled(panel, !isActive);
        });
    };

    modeControls.forEach((control) => {
        control.addEventListener("change", () => {
            if (control.checked) {
                activateMode(control.value);
            }
        });
    });

    activateMode(
        modeControls.find((control) => control.checked)?.value || "manual"
    );
})();
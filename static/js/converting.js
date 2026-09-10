(() => {
    const workspace = document.querySelector(
        "[data-conversion-workspace]"
    );
    const formView = document.querySelector(
        "[data-conversion-form-view]"
    );
    const resultView = document.querySelector(
        "[data-conversion-result-view]"
    );
    const pageHeading = document.querySelector(
        "[data-page-heading]"
    );
    const form = document.querySelector(
        "[data-conversion-form]"
    );
    const submitButton = document.querySelector(
        "[data-conversion-submit]"
    );
    const loading = document.querySelector(
        "[data-conversion-loading]"
    );
    const errorBox = document.querySelector(
        "[data-conversion-error]"
    );

    const characterCount = document.querySelector(
        "[data-character-count]"
    );

    const input = form?.querySelector(
        '[name="input_text"]'
    );

    if (
        !workspace ||
        !formView ||
        !resultView ||
        !pageHeading ||
        !form ||
        !submitButton ||
        !loading ||
        !errorBox ||
        !input ||
        !window.fetch ||
        !window.AbortController
    ) {
        return;
    }

    function updateCharacterCount() {
        if (characterCount) {
            characterCount.textContent =
                String(input.value.length);
        }
    }

    input.addEventListener("input", () => {
        input.setCustomValidity("");
        updateCharacterCount();
    });

    updateCharacterCount();

    // 任意項目の場面だけ、選択中の項目を再度押すと解除できるようにする。
    const sceneRadios = Array.from(
        form.querySelectorAll(
            'input[type="radio"][name="scene"]'
        )
    );
    let activeSceneRadio =
        sceneRadios.find((radio) => radio.checked) ?? null;

    sceneRadios.forEach((radio) => {
        radio.addEventListener("click", () => {
            if (activeSceneRadio === radio) {
                radio.checked = false;
                activeSceneRadio = null;

                radio.dispatchEvent(
                    new Event("input", { bubbles: true })
                );
                radio.dispatchEvent(
                    new Event("change", { bubbles: true })
                );
                return;
            }

            activeSceneRadio = radio;
        });

        radio.addEventListener("change", () => {
            if (radio.checked) {
                activeSceneRadio = radio;
            }
        });
    });

    const initialTitle = workspace.dataset.formTitle ?? "敬語変換画面 | コトバディ";

    let isSubmitting = false;
    let latestRequestId = 0;

    function setLoading(active) {
        isSubmitting = active;
        submitButton.disabled = active;
        loading.hidden = !active;

        formView.inert = active;
        resultView.inert = active;

        workspace.setAttribute("aria-busy", String(active)
        );

        document.documentElement.classList.toggle(
            "is-conversion-loading", active
        );
    }

    function clearError() {
        errorBox.textContent = "";
        errorBox.hidden = true;
    }

    function showError(message) {
        errorBox.textContent = message;
        errorBox.hidden = false;
        errorBox.focus();
    }

    function showForm() {
        clearError();

        resultView.replaceChildren();
        resultView.hidden = true;
        formView.hidden = false;

        pageHeading.textContent = "敬語変換";
        document.title = initialTitle;

        input.focus();
    }

    // 戻る操作でブラウザキャッシュから復元された場合の対策
    window.addEventListener("pageshow", () => {
        setLoading(false);
    });

    // 必須項目、エラーを設定
    async function sendConversionRequest({
        url, payload,
    }) {
        if (isSubmitting) {
            return;
        }

        const requestId = ++latestRequestId;
        const controller = new AbortController();

        let timeOut = false;
        let succeeded = false;

        const timeoutId = window.setTimeout(() => {
            timeOut = true;
            controller.abort();
        }, 45_000);

        setLoading(true);
        clearError();

        try {
            const csrfToken = form.querySelector(
                '[name="csrfmiddlewaretoken"]'
            )?.value ?? "";

            const response = await fetch(url, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify(payload),
                signal: controller.signal,
            });

            const data = await response.json().catch(() => null);

            if (requestId !== latestRequestId) {
                return;
            }

            if (data?.error?.code === "AUTH_REQUIRED") {
                window.dispatchEvent(
                    new Event("conversion:auth-required")
                );
                return;
            }

            if (!response.ok || data?.ok !== true) {
                showError(
                    data?.error?.message ?? "変換できませんでした。"
                );
                return;
            }

            if (
                data?.view?.name !== "result" ||
                typeof data?.view?.html !== "string"
            ) {
                showError(
                    "正しい変換結果を取得できませんでした。"
                );
                return;
            }

            // 成功時にだけ現在の結果を置き換える
            formView.hidden = true;
            resultView.innerHTML = data.view.html;
            resultView.hidden = false;

            pageHeading.textContent = "変換結果";
            document.title =
                data.view.title ?? "変換結果 | コトバディ";

            succeeded = true;
        } catch {
            if (requestId !== latestRequestId) {
                return;
            }

            showError(
                timeOut ? "変換に時間がかかっています。もう一度お試しください。"
                    : "通信に失敗しました。もう一度お試しください。"
            );
        } finally {
            window.clearTimeout(timeoutId);

            if (requestId === latestRequestId) {
                setLoading(false);
            }

            if (succeeded) {
                pageHeading.focus();
            }
        }
    }

    form.noValidate = true;

    form.addEventListener("change", (event) => {
        if (!(event.target instanceof HTMLInputElement)) {
            return;
        }

        if (
            event.target.matches(
                '[name="conversion_mode"], [name="preset_id"]'
            )
        ) {
            clearError();
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (isSubmitting) {
            return;
        }

        clearError();
        input.setCustomValidity("");

        // 入力文章の検証
        if (!input.value.trim()) {
            input.setCustomValidity(
                "変換する文章を入力してください。"
            );
        } else if (input.value.length > 500) {
            input.setCustomValidity(
                "500文字以内で入力してください。"
            );
        }

        if (!input.reportValidity()) {
            return;
        }

        const formData = new FormData(form)

        // ゲストには切り替えUIがないため、未指定はmanual
        const mode =
            formData.get("conversion_mode") === "preset" ? "preset" : "manual";

        const payload = {
            input_text: String(
                formData.get("input_text") ?? ""
            ),
            conversion_mode: mode,
        };

        if (mode === "preset") {
            const presetId = String(
                formData.get("preset_id") ?? ""
            );

            if (!presetId) {
                const hasPresets = Boolean(
                    form.querySelector('input[name="preset_id"]')
                );

                showError(
                    hasPresets ? "プリセットを選択してください。" : "保存済みのプリセットがありません。プリセットを作成してください。"
                );
                return;
            }

            // プリセット時はtargetを送信しない
            payload.preset_id = presetId;
        } else {
            const targetId = String(
                formData.get("target") ?? ""
            );

            if (!targetId) {
                showError("変換タイプを選択してください。");
                return;
            }

            // 手動時はpreset_idを送信しない
            payload.target = targetId;
        }

        // 場面選択は両モード共通の任意項目
        const sceneId = String(formData.get("scene") ?? "");

        if (sceneId) {
            payload.scene = sceneId;
        }

        //その他入力制約も確認
        if (!form.reportValidity()) {
            return;
        }

        await sendConversionRequest({
            url: form.action, payload,
        });
    });



    //閉じるボタン
    resultView.addEventListener("click", (event) => {
        if (!(event.target instanceof Element)) {
            return;
        }

        const closeTrigger = event.target.closest(
            "[data-result-close]"
        );

        if (closeTrigger) {
            event.preventDefault();
            showForm();
        }
    });

    // フィードバックイベント
    resultView.addEventListener(
        "conversion:feedback",
        async (event) => {
            const adjustment = event.detail?.adjustment;

            if (
                adjustment !== "more_formal" &&
                adjustment !== "softer"
            ) {
                return;
            }

            const currentResult = resultView.querySelector(
                "[data-converted-text]"
            );

            if (!currentResult) {
                showError(
                    "現在の変換結果を取得できませんでした。"
                );
                return;
            }

            const formData = new FormData(form);

            const payload = {
                input_text: String(
                    formData.get("input_text") ?? ""
                ),
                current_text: currentResult.textContent.trim(),
                target: String(
                    formData.get("target") ?? ""
                ),
                adjustment,
            };

            const selectedScene = formData.get("scene");

            if (selectedScene) {
                payload.scene = String(selectedScene);
            }

            await sendConversionRequest({
                url: form.dataset.feedbackUrl, payload,
            });
        }
    );
})();

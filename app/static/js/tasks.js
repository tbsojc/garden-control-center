const taskModeButtons =
        document.querySelectorAll(".task-mode-button");

    const executionType =
        document.getElementById("execution_type");

    const onceFields =
        document.getElementById("task-once-fields");

    const recurringFields =
        document.getElementById("task-recurring-fields");

    const automationFields =
        document.getElementById("task-automation-fields");

    const dueDate =
        document.getElementById("task_due_date");

    const intervalDays =
        document.getElementById("interval_days");

    const startMonth =
        document.getElementById("start_month");

    const endMonth =
        document.getElementById("end_month");

    const editExecutionType =
    document.getElementById("edit_execution_type");

    const editOnceFields =
        document.getElementById("edit-task-once-fields");

    const editRecurringFields =
        document.getElementById("edit-task-recurring-fields");

    const editAutomationFields =
        document.getElementById("edit-task-automation-fields");

    const editDueDate =
        document.getElementById("edit_task_due_date");

    const editIntervalDays =
        document.getElementById("edit_interval_days");

    const editStartMonth =
        document.getElementById("edit_start_month");

    const editEndMonth =
        document.getElementById("edit_end_month");


    function updateEditTaskFields() {

        if (!editExecutionType) {
            return;
        }

        const mode = editExecutionType.value;

        editOnceFields.style.display = "none";
        editRecurringFields.style.display = "none";
        editAutomationFields.style.display = "none";

        editDueDate.required = false;
        editIntervalDays.required = false;
        editStartMonth.required = false;
        editEndMonth.required = false;

        if (mode === "once") {
            editOnceFields.style.display = "block";
            editDueDate.required = true;
        }

        if (mode === "recurring") {
            editRecurringFields.style.display = "block";
            editIntervalDays.required = true;
            editStartMonth.required = true;
            editEndMonth.required = true;
        }

        if (mode === "automation") {
            editAutomationFields.style.display = "block";
        }
    }


    if (editExecutionType) {

        editExecutionType.addEventListener(
            "change",
            updateEditTaskFields
        );

        updateEditTaskFields();
    }


    if (
        executionType &&
        onceFields &&
        recurringFields &&
        automationFields &&
        dueDate &&
        intervalDays &&
        startMonth &&
        endMonth
    ) {
        taskModeButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const mode = button.dataset.mode;

                executionType.value = mode;

                taskModeButtons.forEach((item) => {
                    item.classList.remove("active");
                });

                button.classList.add("active");

                onceFields.style.display = "none";
                recurringFields.style.display = "none";
                automationFields.style.display = "none";

                dueDate.required = false;
                intervalDays.required = false;
                startMonth.required = false;
                endMonth.required = false;

                if (mode === "once") {
                    onceFields.style.display = "block";
                    dueDate.required = true;
                }

                if (mode === "recurring") {
                    recurringFields.style.display = "block";
                    intervalDays.required = true;
                    startMonth.required = true;
                    endMonth.required = true;
                }

                if (mode === "automation") {
                    automationFields.style.display = "block";
                }
            });
        });
    }

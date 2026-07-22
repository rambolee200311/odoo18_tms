/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TransportPlan extends Component {
    static template = "wd_tlms.TransportPlanTemplate";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            containers: [],
            calendarDays: [],
            dailyPlans: {},
            currentMonth: new Date(),
            selectedBlNo: '',
            selectedWarehouseId: null,
            blNoOptions: [],
            warehouseOptions: [],
        });

        let dragged = null;

        this.changeMonth = (delta) => {
            const cur = this.state.currentMonth;
            const newDate = new Date(cur.getFullYear(), cur.getMonth(), 1);
            newDate.setMonth(newDate.getMonth() + delta);
            this.state.currentMonth = newDate;
            this.initCalendar();
        };

        onWillStart(async () => {
            await this.loadContainers();
            this.initCalendar();
            await this.loadDailyPlans();
        });

        this.openContainerForm = () => {
            this.action.doAction("wd_tlms.action_bl_container");
        };

        this.onDragStart = (ev, containerId) => {
            dragged = { from: "list", containerId: Number(containerId) };
            ev.dataTransfer.effectAllowed = "move";
            ev.dataTransfer.setData("text/plain", String(containerId));
        };

        this.onDragOver = (ev) => { ev.preventDefault(); ev.dataTransfer.dropEffect = "move"; };

        this.onDrop = async (ev, dateStr) => {
            ev.preventDefault();
            if (!dateStr) { dragged = null; return; }
            const idFromTransfer = Number(ev.dataTransfer.getData("text/plain"));
            const containerId = Number.isFinite(idFromTransfer) && idFromTransfer > 0 ? idFromTransfer : dragged?.containerId;
            if (containerId) {
                // If moving from calendar to another date, delete the old plan first
                if (dragged?.from === "calendar" && dragged?.planId) {
                    await this.orm.call('container.transport.plan', 'delete_transport_plan', [false, dragged.planId]);
                }
                await this.orm.call('container.transport.plan', 'create_transport_plan', [false, containerId, dateStr]);
                await this.loadContainers();
                await this.loadDailyPlans();
            }
            dragged = null;
        };

        this.onPlanDragStart = (ev, planId, containerId, planDate) => {
            ev.stopPropagation();
            dragged = { from: "calendar", planId: Number(planId), containerId: Number(containerId), planDate };
            ev.dataTransfer.effectAllowed = "move";
            ev.dataTransfer.setData("text/plain", String(containerId));
        };

        this.onContainerListDrop = async (ev) => {
            ev.preventDefault();
            const idFromTransfer = Number(ev.dataTransfer.getData("text/plain"));
            const containerId = Number.isFinite(idFromTransfer) && idFromTransfer > 0 ? idFromTransfer : dragged?.containerId;
            if (containerId) {
                const plans = await this.orm.searchRead('container.transport.plan', [['container_id', '=', containerId]], ['id']);
                for (const p of plans) {
                    await this.orm.call('container.transport.plan', 'delete_transport_plan', [false, p.id]);
                }
                await this.loadContainers();
                await this.loadDailyPlans();
            }
            dragged = null;
        };
    }

    async loadContainers() {
        const containers = await this.orm.call("bl.container", "get_unplanned_containers", [false]);
        this.state.containers = containers || [];
        const blNos = [...new Set((containers || []).map(c => c.bl_no).filter(Boolean))].sort();
        this.state.blNoOptions = blNos.map(v => ({ value: v, label: v }));
        const warehouseIds = [...new Set(
            (containers || [])
                .map(c => c.destination_warehouse?.[0])
                .filter(id => Number.isInteger(id) && id > 0)
        )];
        if (warehouseIds.length > 0) {
            const warehouses = await this.orm.read("stock.warehouse", warehouseIds, ["id", "name"]);
            this.state.warehouseOptions = (warehouses || []).map(w => ({ value: w.id, label: w.name }));
        } else {
            this.state.warehouseOptions = [];
        }
    }

    initCalendar() {
        const year = this.state.currentMonth.getFullYear();
        const month = this.state.currentMonth.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const days = [];
        for (let i = 0; i < firstDay.getDay(); i++) days.push({ isEmpty: true, key: `e${i}` });
        for (let d = 1; d <= lastDay.getDate(); d++) {
            const date = new Date(year, month, d);
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
            days.push({
                isEmpty: false, date: d, dateStr: dateStr,
                dayOfWeek: date.getDay(), key: `d${d}`,
            });
        }
        this.state.calendarDays = days;
    }

    async loadDailyPlans() {
        const year = this.state.currentMonth.getFullYear();
        const month = this.state.currentMonth.getMonth();
        const start = new Date(year, month, 1).toISOString().split('T')[0];
        const end = new Date(year, month + 1, 0).toISOString().split('T')[0];
        const summary = await this.orm.call('container.transport.plan', 'get_daily_plan_summary', [false, start, end]);
        this.state.dailyPlans = (summary && typeof summary === "object") ? summary : {};
    }

    getFilteredContainers() {
        let result = this.state.containers;
        if (this.state.selectedBlNo) result = result.filter(c => c.bl_no === this.state.selectedBlNo);
        if (this.state.selectedWarehouseId) result = result.filter(c => c.destination_warehouse?.[0] === this.state.selectedWarehouseId);
        return result;
    }

    onBlNoChange(ev) { this.state.selectedBlNo = ev.target.value; }
    onWarehouseChange(ev) { this.state.selectedWarehouseId = ev.target.value ? parseInt(ev.target.value) : null; }
    clearFilters() { this.state.selectedBlNo = ''; this.state.selectedWarehouseId = null; }

    getDayPlans(dateStr) {
        return this.state.dailyPlans[dateStr] || { count: 0, containers: [] };
    }

    formatMonthYear() {
        const d = this.state.currentMonth;
        return `${d.getFullYear()}年${d.getMonth() + 1}月`;
    }

    getDayClass(day) {
        if (day?.isEmpty) return "o_calendar_day_empty";
        return (day?.dayOfWeek === 0 || day?.dayOfWeek === 6) ? "o_weekend" : "";
    }
}

registry.category("actions").add("tlmp_schedule.action", TransportPlan);
export { TransportPlan };

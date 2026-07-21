import { BarcodeDialog } from '@web/core/barcode/barcode_dialog';
import { Component, onMounted, useRef, useState } from "@odoo/owl";

export class BarcodeInput extends Component {
    static template = "stock_barcode.BarcodeInput";
    static props = {
        onSubmit: {
          type: Function,
          optional: true,
          default: () => console.warn("onSubmit not implemented")
        }
    };

    setup() {
        this.state = useState({
            barcode: false,
        });
        this.inputRef = useRef('manualBarcode');

        onMounted(() => {
          if (this.inputRef.el) this.inputRef.el.focus();
        });
    }

    // 统一处理提交逻辑
    submitBarcode() {
        if (!this.state.barcode) return;

        try {
            if (typeof this.props.onSubmit === "function") {
                this.props.onSubmit(this.state.barcode);
                // 提交后重置输入框
                this.state.barcode = "";
            } else {
                console.error("BarcodeInput: onSubmit prop is not a function");
            }
        } catch (error) {
            console.error("Barcode 提交失败", error);
        }
    }

    _onKeydown(ev) {
        if (ev.key === "Enter") {
            this.submitBarcode();
        }
    }
}

export class ManualBarcodeScanner extends BarcodeDialog {
    static template = "stock_barcode.ManualBarcodeScanner";
    static components = {
        ...BarcodeDialog.components,
        BarcodeInput,
    };

    setup() {
        super.setup();

        // 创建提交处理函数
        this.handleSubmit = (barcode) => {
            // 调用父级回调
            if (typeof this.props.onResult === "function") {
                this.props.onResult(barcode);
            }
            // 关闭对话框
            if (typeof this.props.close === "function") {
                this.props.close();
            } else {
                console.warn("ManualBarcodeScanner: close prop is not a function");
            }
        };
    }

    // 传递给BarcodeInput的属性
    get barcodeInputProps() {
        return {
            onSubmit: this.handleSubmit
        };
    }
}
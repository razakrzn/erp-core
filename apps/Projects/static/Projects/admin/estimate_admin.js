(function () {
  function clearSelect(select, placeholder) {
    select.innerHTML = "";
    select.add(new Option(placeholder, ""));
    select.disabled = true;
  }

  async function loadQuoteItems(projectSelect, itemSelect) {
    const endpoint = projectSelect.dataset.quoteItemsUrl;
    const projectId = projectSelect.value;
    const currentItemId = itemSelect.value;

    if (!endpoint) {
      return;
    }

    if (!projectId) {
      clearSelect(itemSelect, "Select a project first");
      return;
    }

    clearSelect(itemSelect, "Loading items...");

    try {
      const url = new URL(endpoint, window.location.origin);
      url.searchParams.set("project_id", projectId);

      const response = await fetch(url.toString(), {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload = await response.json();
      itemSelect.innerHTML = "";
      itemSelect.add(new Option("---------", ""));

      payload.items.forEach(function (entry) {
        const option = new Option(entry.label, entry.id);
        if (String(entry.id) === String(currentItemId)) {
          option.selected = true;
        }
        itemSelect.add(option);
      });

      itemSelect.disabled = false;
    } catch (error) {
      console.error("Failed to load quote items for project", error);
      clearSelect(itemSelect, "Unable to load items");
    }
  }

  async function loadMaterialStock(materialSelect) {
    const endpoint = materialSelect.dataset.stockUrl;
    const stockValue = document.getElementById("material-stock-value");
    const unitValue = document.getElementById("material-unit-value");

    if (!endpoint || !stockValue || !unitValue) {
      return;
    }

    if (!materialSelect.value) {
      stockValue.textContent = "0";
      unitValue.textContent = "";
      return;
    }

    try {
      const url = new URL(endpoint, window.location.origin);
      url.searchParams.set("product_id", materialSelect.value);

      const response = await fetch(url.toString(), {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload = await response.json();
      stockValue.textContent = payload.stock_on_hand || "0";
      unitValue.textContent = payload.unit || "";
    } catch (error) {
      console.error("Failed to load product stock", error);
      stockValue.textContent = "0";
      unitValue.textContent = "";
    }
  }

  function parseNumber(value) {
    const parsed = Number.parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function updateLabourAmount() {
    const hrsInput = document.getElementById("id_hrs");
    const rateInput = document.getElementById("id_rate");
    const amountValue = document.getElementById("labour-amount-value");

    if (!hrsInput || !rateInput || !amountValue) {
      return;
    }

    const amount = parseNumber(hrsInput.value) * parseNumber(rateInput.value);
    amountValue.textContent = amount.toFixed(2);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const projectSelect = document.getElementById("id_project");
    const itemSelect = document.getElementById("id_item");
    const materialSelect = document.getElementById("id_material");
    const hrsInput = document.getElementById("id_hrs");
    const rateInput = document.getElementById("id_rate");
    const amountValue = document.getElementById("labour-amount-value");

    if (projectSelect && itemSelect) {
      projectSelect.addEventListener("change", function () {
        loadQuoteItems(projectSelect, itemSelect);
      });

      loadQuoteItems(projectSelect, itemSelect);
    }

    if (materialSelect) {
      const refreshMaterialStock = function () {
        loadMaterialStock(materialSelect);
      };

      const $ = window.django && window.django.jQuery ? window.django.jQuery : window.jQuery;
      if ($) {
        $(materialSelect).on("change select2:select select2:clear", refreshMaterialStock);
      } else {
        materialSelect.addEventListener("change", refreshMaterialStock);
      }

      window.addEventListener("load", refreshMaterialStock);
      setTimeout(refreshMaterialStock, 250);
    }

    if (hrsInput && rateInput && amountValue) {
      const refreshLabourAmount = function () {
        updateLabourAmount();
      };

      hrsInput.addEventListener("input", refreshLabourAmount);
      rateInput.addEventListener("input", refreshLabourAmount);
      hrsInput.addEventListener("change", refreshLabourAmount);
      rateInput.addEventListener("change", refreshLabourAmount);
      window.addEventListener("load", refreshLabourAmount);
      setTimeout(refreshLabourAmount, 250);
    }
  });
})();

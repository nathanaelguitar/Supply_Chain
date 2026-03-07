from dataclasses import dataclass

@dataclass
class CompanyFinancials:
    accounts_receivable: float
    inventory: float
    accounts_payable: float
    annual_sales: float
    annual_cogs: float


def days_accounts_receivable(accounts_receivable: float, annual_sales: float) -> float:
    return (accounts_receivable / annual_sales) * 365


def days_inventory(inventory: float, annual_cogs: float) -> float:
    return (inventory / annual_cogs) * 365


def days_accounts_payable(accounts_payable: float, annual_cogs: float) -> float:
    return (accounts_payable / annual_cogs) * 365


def cash_conversion_cycle(financials: CompanyFinancials) -> dict:
    dar = days_accounts_receivable(financials.accounts_receivable, financials.annual_sales)
    di = days_inventory(financials.inventory, financials.annual_cogs)
    dap = days_accounts_payable(financials.accounts_payable, financials.annual_cogs)
    ccc = dar + di - dap

    return {
        "days_accounts_receivable": round(dar, 1),
        "days_inventory": round(di, 1),
        "days_accounts_payable": round(dap, 1),
        "cash_conversion_cycle": round(ccc, 1),
    }


# Example data from the course tool
companies = {
    "Walmart": CompanyFinancials(
        accounts_receivable=5624,
        inventory=44469,
        accounts_payable=38487,
        annual_sales=482130,
        annual_cogs=360984,
    ),
    "P&G": CompanyFinancials(
        accounts_receivable=4861,
        inventory=5454,
        accounts_payable=8257,
        annual_sales=76279,
        annual_cogs=38876,
    ),
    "3M": CompanyFinancials(
        accounts_receivable=4154,
        inventory=3518,
        accounts_payable=1694,
        annual_sales=30274,
        annual_cogs=15383,
    ),
}

for company, financials in companies.items():
    result = cash_conversion_cycle(financials)
    print(f"{company}: {result}")

#output: Walmart: {'days_accounts_receivable': 4.3, 'days_inventory': 45.0, 'days_accounts_payable': 38.9, 'cash_conversion_cycle': 10.3}
#P&G: {'days_accounts_receivable': 23.3, 'days_inventory': 51.2, 'days_accounts_payable': 77.5, 'cash_conversion_cycle': -3.1}
#3M: {'days_accounts_receivable': 50.1, 'days_inventory': 83.5, 'days_accounts_payable': 40.2, 'cash_conversion_cycle': 93.4}


from dataclasses import dataclass

@dataclass
class ProcessData:
    theoretical_flow_time: float   # pure processing time
    actual_flow_time: float        # observed time including delays

def efficiency_loss(data: ProcessData) -> dict:
    loss = data.actual_flow_time - data.theoretical_flow_time
    loss_pct = loss / data.actual_flow_time

    efficiency = data.theoretical_flow_time / data.actual_flow_time

    return {
        "theoretical_flow_time": data.theoretical_flow_time,
        "actual_flow_time": data.actual_flow_time,
        "efficiency_loss_time": round(loss, 2),
        "efficiency_loss_percent": round(loss_pct * 100, 2),
        "process_efficiency": round(efficiency * 100, 2)
    }

# Example scenario
example = ProcessData(
    theoretical_flow_time=18,   # minutes of pure work
    actual_flow_time=30         # total observed time
)

result = efficiency_loss(example)

print(result)
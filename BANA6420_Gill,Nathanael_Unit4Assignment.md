# BANA 6420 Unit 4 Assignment

**Student:** Gill, Nathanael  
**Assignment:** Employing a Holistic Approach to Supply Chain Design  
**Primary data source:** `data/u4_sec_api_results_2016_2021.csv`  
**Tag traceability file:** `data/u4_sec_api_tag_audit.csv`

## Part One: Measuring and Improving Supply Chain Cash Flow Efficiency

### Solution steps

To complete Part One, I pulled the financial statement data for 3M, P&G, and Walmart for fiscal years 2016 through 2021 from the SEC EDGAR XBRL API using `sec_api_u4.py`, then saved the results in `data/u4_sec_api_results_2016_2021.csv`. I used accounts receivable, inventory, accounts payable, annual sales, and annual cost of goods sold as the base inputs for the working capital analysis. From those values, I calculated days of accounts receivable as `(Accounts Receivable / Annual Sales) * 365`, days of inventory as `(Inventory / Annual COGS) * 365`, and days of accounts payable as `(Accounts Payable / Annual COGS) * 365`. I then computed the cash conversion cycle as `DAR + DI - DAP`. Because SEC filers do not always report the same concept under one perfectly consistent XBRL tag, I merged candidate tags in a defined priority order and kept the most recently filed 10-K value for each fiscal year. For presentation, I converted the dollar values from raw USD into USD millions so the results are easier to read and compare across companies.

### Computed metrics table

All monetary values are shown in USD millions.

| company | year | Accounts Receivable | Inventory | Accounts Payable | Annual Sales | Annual COGS | Days of Accounts Receivable | Days of Inventory | Days of Accounts Payable | Cash Conversion Cycle |
|---|---|---|---|---|---|---|---|---|---|---|
| 3M COMPANY | 2016 | 4,392 | 3,385 | 1,798 | 30,109 | 15,118 | 53.24 | 81.73 | 43.41 | 91.56 |
| 3M COMPANY | 2017 | 4,911 | 4,034 | 1,945 | 31,657 | 16,055 | 56.62 | 91.71 | 44.22 | 104.12 |
| 3M COMPANY | 2018 | 5,020 | 4,366 | 2,266 | 32,765 | 16,682 | 55.92 | 95.53 | 49.58 | 101.87 |
| 3M COMPANY | 2019 | 4,791 | 4,134 | 2,228 | 32,136 | 17,136 | 54.42 | 88.05 | 47.46 | 95.01 |
| 3M COMPANY | 2020 | 4,705 | 4,239 | 2,561 | 32,184 | 16,605 | 53.36 | 93.18 | 56.29 | 90.24 |
| 3M COMPANY | 2021 | 4,660 | 4,985 | 2,994 | 35,355 | 18,795 | 48.11 | 96.81 | 58.14 | 86.77 |
| PROCTER & GAMBLE CO | 2016 | 4,373 | 4,716 | 9,325 | 65,299 | 32,909 | 24.44 | 52.31 | 103.43 | -26.68 |
| PROCTER & GAMBLE CO | 2017 | 4,594 | 4,624 | 9,632 | 65,058 | 32,535 | 25.77 | 51.88 | 108.06 | -30.41 |
| PROCTER & GAMBLE CO | 2018 | 4,686 | 4,738 | 10,344 | 66,832 | 34,268 | 25.59 | 50.47 | 110.18 | -34.12 |
| PROCTER & GAMBLE CO | 2019 | 4,951 | 5,017 | 11,260 | 67,684 | 34,768 | 26.70 | 52.67 | 118.21 | -38.84 |
| PROCTER & GAMBLE CO | 2020 | 4,178 | 5,498 | 12,071 | 70,950 | 35,250 | 21.49 | 56.93 | 124.99 | -46.57 |
| PROCTER & GAMBLE CO | 2021 | 4,725 | 5,983 | 13,720 | 76,118 | 37,108 | 22.66 | 58.85 | 134.95 | -53.45 |
| Walmart Inc. | 2016 | 5,624 | 44,469 | 38,487 | 478,614 | 360,984 | 4.29 | 44.96 | 38.92 | 10.34 |
| Walmart Inc. | 2017 | 5,835 | 43,046 | 41,433 | 481,317 | 361,256 | 4.42 | 43.49 | 41.86 | 6.05 |
| Walmart Inc. | 2018 | 5,614 | 43,783 | 46,092 | 495,761 | 373,396 | 4.13 | 42.80 | 45.06 | 1.88 |
| Walmart Inc. | 2019 | 6,283 | 44,269 | 47,060 | 510,329 | 385,301 | 4.49 | 41.94 | 44.58 | 1.85 |
| Walmart Inc. | 2020 | 6,284 | 44,435 | 46,973 | 519,926 | 394,605 | 4.41 | 41.10 | 43.45 | 2.06 |
| Walmart Inc. | 2021 | 6,516 | 44,949 | 49,141 | 555,233 | 420,315 | 4.28 | 39.03 | 42.67 | 0.64 |

### Patterns observed and possible explanations

The clearest pattern in the data is that each company operates with a very different working capital model, and those differences line up closely with the economics of its industry. 3M carries the highest cash conversion cycle over the full period, generally between the high 80s and low 100s in days. That makes sense because 3M is a diversified manufacturer selling to business customers, so it extends trade credit and also needs to hold a wide range of inventory across product lines. Its cash conversion cycle trends down modestly over time, which appears to be driven less by faster collections or lower inventory and more by rising days of accounts payable. In other words, 3M seems to be offsetting part of its working capital burden by stretching supplier payment timing.

P&G shows the opposite profile. Its cash conversion cycle is negative in every year and becomes even more negative from 2016 to 2021. That is an important result because it means the company is generally collecting cash from customers before it pays suppliers. The main driver is the steady increase in days of accounts payable, which rises above 130 days by 2021, while receivables remain fairly low and inventory stays moderate. From a supply chain finance perspective, this suggests that P&G's scale and bargaining power allow it to use supplier terms as a structural financing advantage. That kind of pattern is typical of a dominant branded consumer goods company with strong retailer relationships and access to formal supply chain finance tools.

Walmart's pattern is different again. Its cash conversion cycle stays close to zero and declines to less than one day by 2021. That is exactly what a well-run high-volume retailer should look like. Walmart collects cash from consumers almost immediately, so receivables are minimal, while its inventory and payables move at roughly similar speeds. The result is a very tight operating cycle where the company is not tying up cash for long. That outcome reflects Walmart's business model, especially fast inventory flow, strong logistics execution, and purchasing power with suppliers.

Looking across all three companies, one broader pattern is that days of accounts payable increase over time in each case. That suggests a wider market trend in which large firms have become more aggressive about extending supplier payment terms. The 2020 period also shows some effects that are plausibly tied to pandemic conditions. P&G's receivables days improve sharply, Walmart remains stable despite major disruption, and 3M appears to benefit from demand shifts tied to safety and industrial products. Overall, the data shows that cash flow efficiency is not just an accounting outcome. It is a direct reflection of channel structure, bargaining power, operating model, and supply chain design.

## Part Two: Designing a Strategy to Achieve Supply Chain Coordination

### Chosen company

Walmart

### Current practices in achieving supply chain coordination

I chose Walmart because it is one of the clearest real-world examples of supply chain coordination at scale. Its coordination model is not based on one tool, but on a system of reinforcing practices. A major part of that system is Walmart's Every Day Low Price and Every Day Low Cost philosophy, which reduces the promotional spikes that often create distorted demand signals upstream. That matters because stable retail pricing helps suppliers plan production more accurately and reduces the bullwhip effect. Walmart also has a long history of vendor-managed inventory relationships, where suppliers use actual inventory and sales information to manage replenishment instead of reacting only to purchase orders. That shifts the supply chain from delayed, order-based coordination to demand-based coordination.

Walmart strengthens that model through data transparency and operating discipline. Its Retail Link platform gives suppliers near real-time visibility into point-of-sale and inventory information, which reduces information asymmetry and improves planning quality. Collaborative planning, forecasting, and replenishment practices then build on that visibility by making demand planning a shared process rather than a disconnected one. On the physical side, Walmart's cross-docking network reduces storage time and keeps inventory moving quickly through the system, which improves both cost performance and responsiveness. Finally, Walmart uses supplier scorecards and operational metrics such as fill rate and on-time delivery to create accountability. Taken together, these practices show that Walmart does not treat coordination as a soft relationship concept. It treats coordination as a measurable operating capability supported by data, process discipline, and incentives.

### Recommendations for improved supply chain management

Even though Walmart is already highly advanced, I think its next gains will come from improving incentive alignment rather than simply collecting more data. One recommendation is to move beyond standard wholesale-price contracts in selected categories and pilot revenue-sharing, buyback, or quantity-flexibility contracts where demand is uncertain. In classes of products such as seasonal items, apparel, and perishables, those contract structures could reduce the mismatch between retailer and supplier incentives and lead to better service levels with less waste. From a course concepts standpoint, this is important because coordination problems usually persist even when information sharing is strong if the economic incentives are still misaligned.

I would also recommend deeper investment in short-horizon demand sensing and multi-tier visibility. Walmart already has excellent first-tier data, but the next frontier is using machine learning models that combine point-of-sale signals with weather, local events, social signals, and regional demand patterns. Better short-term forecasts would improve replenishment decisions and help suppliers respond more intelligently. At the same time, Walmart should push visibility deeper into Tier 2 and Tier 3 suppliers so that disruptions can be identified before they surface as stockouts. Finally, Walmart should connect its coordination system more directly to supplier incentives tied to sustainability and resilience. If preferred placement, contract renewal, or commercial advantages depend not only on service metrics but also on traceability, carbon performance, and disruption readiness, Walmart can align operational coordination with broader strategic goals instead of treating them as separate agendas.

## Part Three: Designing a Strategy for Supply Chain Sustainability

### Chosen company

Procter & Gamble (P&G)

### Current practices in achieving supply chain sustainability

For Part Three, I chose Procter & Gamble because it is large enough that its sustainability choices affect a broad global supplier network, yet it also faces the classic challenge of managing impacts that sit far beyond its own factories. P&G has built a substantial sustainability platform under its Ambition 2030 framework, including renewable electricity adoption in major operating regions and long-term emissions goals for direct operations. It has also made formal sourcing commitments in categories such as palm oil and pulp, where environmental risk is especially visible. In packaging, the company has pushed on recyclability, reuse, and reductions in virgin plastic, while also experimenting with refill models and more recycled content.

What stands out to me is that P&G's current approach covers the main themes stakeholders expect to see: energy, packaging, water, sourcing, and supplier engagement. The company also uses supplier sustainability scorecards, which is important because it signals that sustainability is not being treated as a standalone public relations issue. Instead, it is at least partially embedded in procurement and supplier management. At the same time, the company still faces a common consumer goods problem: a large share of its environmental footprint sits in upstream suppliers and downstream product use, not just within its own direct operations. That means the program is meaningful, but it also means the hardest work is still in the broader value chain.

### Recommendations for improved supply chain management

My main recommendation is that P&G should shift from a sustainability model that is mostly commitment-driven to one that is more value-chain specific, measurable, and enforced through supplier economics. The biggest issue is Scope 3 emissions. Since most of P&G's footprint lies outside its direct operations, stronger supplier decarbonization requirements and clearer milestone-based targets are necessary. That means going beyond broad scorecards and building supplier programs that include technical support, financing mechanisms, and practical pathways for smaller suppliers to adopt renewable energy or lower-carbon inputs. If P&G wants material progress, it has to make sustainability operational rather than symbolic.

I also think P&G should push harder on circular design and deeper traceability. Incremental packaging improvements are useful, but they are not enough if the underlying system still depends heavily on hard-to-recycle materials and weak collection infrastructure. A stronger strategy would combine product redesign, support for extended producer responsibility systems, and direct investment in recovery and recycling capabilities. On the sourcing side, P&G should strengthen traceability in palm oil, paper, and other forest-risk materials through deeper tier mapping and real monitoring tools rather than relying too heavily on certification alone. Finally, more transparent disclosure would improve credibility. If the company reports more clearly on supplier tiers, progress milestones, and areas where performance is lagging, it will be easier for investors, regulators, and customers to judge whether the sustainability strategy is driving real supply chain change.

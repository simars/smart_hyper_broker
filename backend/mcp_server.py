from mcp.server.fastmcp import FastMCP
import normalization

# Initialize FastMCP Server defining the Intelligence Context mapping
mcp = FastMCP("SmartHyperBroker")

@mcp.tool()
def get_normalized_portfolio() -> list:
    """
    Returns the user's complete unified investment portfolio securely across all active brokerage accounts.
    Output includes real-time FX-converted metrics mapping 'market_val', 'open_pnl', 'closed_pnl', 
    and explicit native account parameters (TFSA, RRSP, Margin, etc).
    Use this payload to form rigorous analytics regarding over-concentration or manager biases.
    """
    return normalization.get_normalized_positions()

@mcp.prompt("manager_thesis_validation")
def manager_thesis_validation_prompt() -> str:
    """
    A foundational prompt to extract structural Macro Thesis evaluations iteratively from an LLM against the current portfolio.
    """
    return (
        "You are an expert Wall Street algorithmic portfolio analyst. "
        "Please utilize the `get_normalized_portfolio` tool to extract the user's entire live holding matrix right now. "
        "Review the asset allocations, weightings, and structural exposure. "
        "Systematically validate if their current allocations match a defensible long-term macro-thesis (e.g., Tech-heavy, Fixed-Income hedge, High-Yield), "
        "and call out structural gaps or actionable adjustments they should make to fortify their macro stance."
    )

@mcp.prompt("behavioral_bias_report")
def behavioral_bias_prompt() -> str:
    """
    A foundational prompt to automatically identify psychological biases anchoring the user's portfolio.
    """
    return (
        "You are an expert Behavioral Finance analyst. "
        "Please utilize the `get_normalized_portfolio` tool to parse the user's complete Open (Unrealized) and Closed (Realized) PnL history. "
        "Review the metrics to detect psychological blind spots. Look specifically for: "
        "\n1. Sunk-Cost Fallacy: Holding massive open losses (`open_pnl` deeply negative) without closing to avoid realizing failure. "
        "\n2. Home-Country Bias: Sizable over-allocation exclusively to CAD assets instead of global diversification. "
        "\n3. Concentration Risk: Giant weightings attached to singular volatile assets vs broad indexes. "
        "\nExplicitly outline these biases using the exact data presented and recommend rigid behavioral corrections."
    )

from fastmcp import FastMCP

from affiliate_mktg.src.core.models import SearchInput
from affiliate_mktg.src.links.links_manager import LinksManager

mcp_server = FastMCP(name="AffiliateMarketingBlogPostMCPServer")


@mcp_server.tool(name="generate_link_post_blog_manual_tool")
async def generate_link_post_blog_manual_tool(searchInput: SearchInput):
    try:
        linksManager = LinksManager()
        result = await linksManager.generate_link_post_blog_manual(
            searchInput=searchInput
        )

        success = result.get("success", False)
        content = result.get("content", "")
        if success:
            return {
                "status": "Processed",
                "success": success,
                "content": "Blog Generated and Posted.",
            }
        return {
            "status": "Processed",
            "success": success,
            "content": content,
        }

    except Exception as e:
        return {
            "status": "Failure",
            "count": 0,
            "results": None,
            "success": False,
            "content": f"Amazon Affiliate marketing links NOT Generated and Posted : {e}",
        }


if __name__ == "__main__":
    mcp_server.run()
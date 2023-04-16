import requests
import json
from nextcord.ext.commands import Cog
from nextcord.ext import tasks

# Todo*: Add statcord to elli

class topgg(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijc2Mzc3ODE2ODgyNTA1MzI1NCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjgxMjQ1Mjc3fQ.zSEvnLZ5ObsudetjbLyOAUfQAaAPs8uD1HhnpuFkJyw'
        self.update_stats.start()
        self.baseURL = "https://top.gg/api/"

    @tasks.loop(hours=1)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        
        if self.bot.user.id == 1086789440044806174:
            return

        try:
            server_count = len(self.bot.guilds)
            payload = {"server_count": server_count}
            r = self.sendPostRequest(f"bots/{self.bot.user.id}/stats", payload)

            if r.status_code in [504, 408]:
                return

            if r.status_code != 200:
                print(f"Failed to post server count\nStatus Code: {r.status_code}\nResponse: {r.text}")

        except Exception as e:
            print(f'Failed to post server count\n{type(e).__name__}: {e}')
            
    def sendPostRequest(self, endpoint, data) -> requests.Response:
        url = f"{self.baseURL}{endpoint}"
        
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        
        data = json.dumps(data)
        
        try:
            json.loads(data)
        except json.decoder.JSONDecodeError:
            print(f"Data is not valid json\n{data}")
            return
        
        return requests.post(url, data=data, headers=headers)

def setup(bot):
	bot.add_cog(topgg(bot))
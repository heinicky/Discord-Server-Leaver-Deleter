import requests, json
from console import console

console = console()

excluded_servers = []

def getheaders(token=None):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0'
        }
    if token:
        headers.update({'Authorization': token})
    return headers


class Leaver:
    def __init__(self, delete_owned_servers: bool, token: str):
        if delete_owned_servers == True:
            self.deleteowned = True
        else:
            self.deleteowned = False
        login = requests.get('https://discord.com/api/v9/users/@me', headers=getheaders(token))
        if login.status_code == 200:
            console.print_logo(login.json()['username'])
            self.token = token
            self.userid = int(login.json()['id'])
        else:
            console.error('Invalid Token. Press Enter to Exit.')
            input()
            exit()
    
    def leave_server(self, serverid: int):
        guildinfo = requests.get(f'https://discord.com/api/v9/guilds/{serverid}', headers=getheaders(self.token)).json()
        if int(guildinfo['owner_id']) == self.userid:
            if self.deleteowned:
                delete = requests.post(f'https://discord.com/api/v9/guilds/{serverid}/delete', headers=getheaders(self.token), json={})
                if delete.status_code == 204:
                    console.log(f'Deleted Server {guildinfo["name"]}')
                else:
                    console.error(f'Could Not Delete {guildinfo["name"]}')
            else:
                return
        else:
            leave = requests.delete(f'https://discord.com/api/v9/users/@me/guilds/{serverid}', headers=getheaders(self.token), json={'lurking':False})
            if leave.status_code == 204:
                console.log(f'Left {guildinfo["name"]}')
            else:
                console.error(f'Could Not Leave Server {guildinfo["name"]}')

def main(delete_servers: bool, token: str, exclude: bool):
    serverstoleave = []
    leaver = Leaver(delete_owned_servers=delete_servers, token=token)
    if exclude: 
        with open('excludeservers.txt', 'r', encoding='utf-8') as serverlist:
            servers = serverlist.read().splitlines()
            if len(servers) > 0:
                for serverid in servers:
                    try:
                        excluded_servers.append(int(serverid))
                    except:
                        console.error('Invalid Server ID in excludedservers.txt')
            else:
                if not len(excluded_servers) > 0:
                    console.error('No Server IDs Found in excludedservers.txt')
                    exclude = False

        serverlist.close()
    guilds = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=getheaders(token)).json()

    for item in guilds:
        if int(item["id"]) not in excluded_servers:
            serverstoleave.append(item["id"])
        else:
            console.info(f'Ignored {item["id"]} because its in excluded list')

    for server in serverstoleave:
        leaver.leave_server(server)

    console.log('Finished Leaving')
    
if __name__ == '__main__':
    settings = json.load(open('config.json'))
    token = settings['token']
    if token == 'TOKEN_HERE':
        console.error('edit config.json to include your token.')
        input()
        exit()
    main(delete_servers=settings['delete_owned_servers'], token=token, exclude=settings['exclude_servers'])

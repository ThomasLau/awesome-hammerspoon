--- === BingDaily ===
---
--- Use Bing daily picture as your wallpaper, automatically.
---
--- Download: [https://github.com/Hammerspoon/Spoons/raw/master/Spoons/BingDaily.spoon.zip](https://github.com/Hammerspoon/Spoons/raw/master/Spoons/BingDaily.spoon.zip)

local obj={}
obj.__index = obj

-- Metadata
obj.name = "BingDaily"
obj.version = "1.0"
obj.author = "ashfinal <ashfinal@gmail.com>"
obj.homepage = "https://github.com/Hammerspoon/Spoons"
obj.license = "MIT - https://opensource.org/licenses/MIT"

local function curl_callback(exitCode, stdOut, stdErr)
    if exitCode == 0 then
        obj.task = nil
        obj.last_pic = hs.http.urlParts(obj.full_url).lastPathComponent
        -- local localpath = os.getenv("HOME") .. "/Public/bing/" .. hs.http.urlParts(obj.full_url).lastPathComponent
        local localpath = os.getenv("HOME") .. "/Public/bing/" .. hs.http.urlParts(obj.full_url).queryItems[1].id
        hs.console.printStyledtext("desktopIMG:" .. localpath)
        -- hs.screen.mainScreen():desktopImageURL("file://" .. localpath)
        hs.screen.primaryScreen():desktopImageURL("file://" .. localpath)
        local scs=hs.screen.allScreens()

        local count = 0
        for _ in pairs(scs) do count = count + 1 end
        hs.console.printStyledtext("table.size: " .. count)
        for i=1,#scs do scs[i]:desktopImageURL("file://" .. localpath) end
    else
        print(stdOut, stdErr)
    end
end

local function bingRequest()
    -- local user_agent_str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4"
    -- local user_agent_str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"
    local user_agent_str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    local json_req_url = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1"

    local hh={["User-Agent"]=user_agent_str}
    if math.random(2)==1 then hh["cookie"]="ENSEARCH=BENVER=1" end
    hs.http.asyncGet(json_req_url, hh, function(stat,body,header)
        if stat == 200 then
            if pcall(function() hs.json.decode(body) end) then
                local decode_data = hs.json.decode(body)
                local pic_url = decode_data.images[1].url
                local pic_name = hs.http.urlParts(pic_url).lastPathComponent
                if obj.last_pic ~= pic_name then
                    obj.full_url = "https://www.bing.com" .. pic_url
                    if obj.task then
                        obj.task:terminate()
                        obj.task = nil
                    end
                    -- local localpath = os.getenv("HOME") .. "/Public/bing/" .. hs.http.urlParts(obj.full_url).lastPathComponent
                    local localpath = os.getenv("HOME") .. "/Public/bing/" .. hs.http.urlParts(obj.full_url).queryItems[1].id
                    obj.task = hs.task.new("/usr/bin/curl", curl_callback, {"-A", user_agent_str, obj.full_url, "-o", localpath})
                    obj.task:start()
                end
            end
        else
            print("Bing URL request failed!")
        end
    end)
end

function obj:init()
    if obj.timer == nil then
        obj.timer = hs.timer.doEvery(3*60*60, function() bingRequest() end)
        obj.timer:setNextTrigger(5)
    else
        obj.timer:start()
    end
end

return obj

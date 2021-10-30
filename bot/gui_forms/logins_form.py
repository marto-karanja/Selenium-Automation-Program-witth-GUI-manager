import wx

class LoginFrame(wx.Frame):

    def __init__(self, parent, launcher):
        
        wx.Frame.__init__(self, parent, id = -1, title = 'Save Essay Shark Logins',
                size=(340, 200))
        self.launcher = launcher
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour("White")
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        #self.createMenuBar()
        self.createButtonBar(panel, yPos = 120)
        self.createTextFields(panel)

    def menuData(self):
        return (("&File",
                    ("&Open", "Open in status bar", self.OnOpen),
                    ("&Quit", "Quit", self.OnCloseWindow)),
                ("&Edit",
                    ("&Copy", "Copy", self.OnCopy),
                    ("C&ut", "Cut", self.OnCut),
                    ("&Paste", "Paste", self.OnPaste),
                    ("", "", ""),
                    ("&Options...", "DisplayOptions", self.OnOptions)))

    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def createMenu(self, menuData):
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    def buttonData(self):
        return (("Save Logins", self.OnSave),)

    def createButtonBar(self, panel, yPos = 0):
        xPos = 135
        for eachLabel, eachHandler in self.buttonData():
            pos = (xPos, yPos)
            button = self.buildOneButton(panel, eachLabel, eachHandler, pos)
            xPos += button.GetSize().width

    def buildOneButton(self, parent, label, handler, pos=(0,0)):
        button = wx.Button(parent, -1, label, pos)
        self.Bind(wx.EVT_BUTTON, handler, button)
        return button

    def textFieldData(self):
        return (("Email:", (10, 50), self.launcher.user_details['email'], "email"),
                ("Password:", (10, 80),  self.launcher.user_details['password'], "password"))

    def createTextFields(self, panel):
        self.text_field ={}
        for eachLabel, eachPos, user_detail, field_name in self.textFieldData():
            text_field = self.createCaptionedText(panel, eachLabel, eachPos, user_detail, field_name)
            self.text_field [field_name] = text_field

    def createCaptionedText(self, panel, label, pos, user_detail, field_name):
        static = wx.StaticText(panel, -1, label, pos)
        static.SetBackgroundColour("White")
        textPos = (pos[0] + 55, pos[1])
        text_field = wx.TextCtrl(panel, -1, size=(200, -1), pos=textPos, value=user_detail, name=field_name)
        return text_field

    # Just grouping the empty event handlers together

    def OnSave(self, event):
        email = self.text_field['email'].GetValue()
        password = self.text_field['password'].GetValue()

        self.launcher.save_user_details(email, password)
        self.launcher.user_details = self.launcher.fetch_user_details()

        # close window after successful save
        self.OnCloseWindow(event)


    def OnCloseWindow(self, event):
        self.Destroy()


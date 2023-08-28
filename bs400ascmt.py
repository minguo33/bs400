#!/usr/bin/env python3


#You can't run asciimatics from IDLE.  You have to use the command line.
import os

from asciimatics.widgets import Frame, TextBox, Layout, Label, Divider, Text, \
    CheckBox, RadioButtons, Button, PopUpDialog, TimePicker, DatePicker, DropdownList, PopupMenu, MultiColumnListBox, ListBox
from asciimatics.effects import Background
from asciimatics.event import MouseEvent
from asciimatics.event import KeyboardEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication, \
    InvalidFields
from asciimatics.parsers import AsciimaticsParser
import sys
import re
import datetime
#import logging

import subprocess


#You can't run asciimatics from IDLE.  You have to use the command line.


#This has a logging file.  Pretty cool.
#logging.basicConfig(filename="forms.log", level=logging.DEBUG)


class DemoFrame(Frame):
    def __init__(self, screen):
        super(DemoFrame, self).__init__(screen,
                                        int(screen.height * 2 // 2),
                                        int(screen.width * 2 // 2 ),
                                        #data=form_data,
                                        has_shadow=True,
                                        name="Main Form",
                                        title ="BS 400")
        self.table_height = screen.height-10
        self.searchlayout = Layout([1, 5, 1])
        self.add_layout(self.searchlayout)        
        layout = Layout([1, 18, 1], fill_frame=True)
        self.add_layout(layout)

        self._reset_button = Button("Reset", self._reset)

        self.searchlayout.add_widget(Label("Press enter To Search.  Arrow Keys and Tab move between areas."), 1)
        self.pole_search =Text(label=">",
                               name="polesearch"
                               , on_change=self._on_pole_change
                              ,validator="^[0-9]*$")
        self.search_list = ListBox(height = 3, options=[('Pole', 1),('SO', 2)], centre = True, label = 'Search by', name = 'stype', parser = None, on_change = self._set_search_type, on_select = None, validator = None)

        self.searchlayout.add_widget(Label(""),0)
        self.search_cat = Label("")
        #self.searchlayout.add_widget(self.search_cat, 0)        
        self.searchlayout.add_widget(self.search_list,2)
        self.searchlayout.add_widget(self.pole_search,1)

        #self.searchlayout.add_widget(, 2)
        

       # layout.add_widget(Button("Search", self._on_search
       #                 ),1
       #                 )
        self.results = MultiColumnListBox(
                            height=screen.height-10,
                            #titles =['Pole#','W.o.#', 'Id','Prfx','PLength','Units','Span','No.Wires','WSize','WType','Pri/sec','CloseoutDate'],
                            titles = ['GPOLE#', 'GPREFX','GYEAR','GPCOD','GLENTH','GSPAN','GWIRE','GPSIZE', 'GTYPE', 'GSWIRE', 'GSSIZE', 'GSTYPE', 'AUs'],
                          #columns=[10,10,5,5,8,0,10,10,10,10,10,7,10],
                            columns=[10,10,5,5,8,5,10,10,10,10,10,7,0],
                          options=[([], 1),(['Select', 'a row to ', 'See', 'a','detail', 'menu.  Large Results will scroll'], 2)],
                          label = 'Results',
                          name = 'Table',
                            add_scroll_bar = True,
                            on_change = self._on_change_upd,
                          on_select = self._on_select_pop
                            )
        #self.results.custom_colour = 'invalid'
        self.old_results = None
        self.mode = True  #TRue for search poles from the reslts table, False for search SOs from the Results table.
        
        layout.add_widget(self.results,1)

        layout.add_widget(Divider(height=3), 1)

        self.layout1 = layout
        layout1_5 = Layout([1,1,1])
        
        self.add_layout(layout1_5)
        layout1_5.add_widget(Label("Results appear in the Table. Select a record to access SO#"), 1)
        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(self._reset_button, 0)
        #layout2.add_widget(Button("View Data", self._view), 1)
        layout2.add_widget(Button("Quit", self._quit), 2)

        self.fix()
        self.save()

    def _set_search_type(self):
        print('changed', self, self.search_list.value)
        if self.search_list.value == 1:
            self.search_cat.text = "Search by Pole #"
            self.mode = 1
        else:
            self.search_cat.text = "Search by SO #"
            self.mode = -1
        

    def process_event(self, event):
        # Handle dynamic pop-ups now.
        # Return button is keyboard event 13

        if (event is not None and isinstance(event, MouseEvent) and
                event.buttons == MouseEvent.DOUBLE_CLICK):
            # By processing the double-click before Frame handling, we have absolute coordinates.
            options = [
                ("Default", self._set_default),
                ("Green", self._set_green),
                ("Monochrome", self._set_mono),
                ("Bright", self._set_bright),
            ]
            if self.screen.colours >= 256:
                options.append(("Red/white", self._set_tlj))
            self._scene.add_effect(PopupMenu(self.screen, options, event.x, event.y))
            event = None
        if isinstance(event, KeyboardEvent):
            #Process Return button if the focused widget is the pole text entry
            if event.key_code == 13 and self.pole_search == self.searchlayout.get_current_widget() :
                def search_setup(var):

                    print(var)

                
##                self._scene.add_effect(
##                PopUpDialog(screen=self._screen
##                          #, [('Go To Work Order', self._on_pole_change), ('Go to Pole Detail', self._on_pole_change)]
##                          , text="Search by what?"
##                          , buttons =['Search by Pole#', 'Search by SO#']
##                          #, round(self.screen.width/2)
##                          #,  round(self.screen.height/2)
##                          , has_shadow = True
##                            #, on_close = self._set_so_records
##                            , on_close =  search_setup
##                        )
##                    )
                if self.search_list.value == 1:
                    self._on_search()
                    self.mode = True
                else:
                    try:
                        search_string =  str(int(self.pole_search.value))
                        search_string = search_string  
                    except:
                        search_string = self.pole_search.value
                        search_string = search_string  
                    
                    self._control_recs(1, search_string)
        

        # Pass any other event on to the Frame and contained widgets.
        return super(DemoFrame, self).process_event(event)

    def _set_default(self):
        self.set_theme("default")

    def _set_green(self):
        self.set_theme("green")

    def _set_mono(self):
        self.set_theme("monochrome")

    def _set_bright(self):
        self.set_theme("bright")

    def _set_tlj(self):
        self.set_theme("tlj256")

    def _set_so_records(self, progs):
        selected = self.results.options[self.results.value-1]
        
        stringer = "'" + selected[0][1] + "%'"

        columns = "[Pole#], [W.o.#],[Prfx],[PoleCode],[PLength],[Units] "
        progs = 'X:\\Engineering\\GIS\\SOFTWARE\\trdsql_v0.7.6_windows_amd64\\trdsql.exe -ih -id "\t"  -oh -ocsv "select ' + columns + ' from X:\Engineering\GIS\AS400\BS400_db\MXPCPR_hdr.TXT where [W.o.#] like ' + stringer + ' order by cast([Pole#]as int), [W.o.#]'
        
        result = subprocess.run(progs, shell=True, capture_output=True, text=True)
        
        #Turn result into a list  based on newline category
        result = str(result.stdout).split("\n")

        #Turn result into a list of lists based on comma separated value.
        x = 0
        res = []
        for x in range(len(result)):
            a = result[x].split(',')
            result[x] = a
            res.append((a,x+1))


        #Save the old table contents
        self.old_results = self.results.options            
        
        self.results.options = res
        
        return 

    def _control_recs(self, self2, payload = None):
         
        
        selected =  self.results.options[self.results.value-1]
        if self2 == 0 :
            pass
            #Go Back to previous reuslts

            #restore old values
            #self.results.options = self.old_results or self.results.options

        elif self2 ==3:
            self.results.options = self.old_results or self.results.options
        elif self2 ==1:
            args = 'X:\\Engineering\\GIS\\SOFTWARE\\trdsql_v0.7.6_windows_amd64\\trdsql.exe -ih -id "\t" -ocsv -oraw "select ' 
            columns = "[Pole#], [W.o.#],case when [Id] like 3 then '+' when [Id] like 4 then '-' else [Id] end  as ac, [Prfx],[PLength],[Units], [Span],[No.Wires],[WSize], [WType], [Pri/sec], [CloseoutDate]"
            #columns = ["Pole#", "W.o.#","Id","Prfx","PLength","Units", "Span","No.Wires","WSize", "WType", "Pri/sec", "CloseoutDate" ]
            table = ' from X:\Engineering\GIS\AS400\BS400_db\MXPCPR_hdr.TXT '
            if self.mode > 0 or self.mode < -1:
                where = 'where [Pole#] like '
                search_string = selected[0][0]
                orderby  = ' ' #None
                self.pole_search.value = selected[0][0]
            else:
                #Expand Poles on Desired SO#
                where = 'where [W.o.#] like '
                #where = 'where [Pole#] like '
                search_string = payload or selected[0][1]
                orderby  = ' ' #None
                self.pole_search.value =""

            print(args + columns + table)
            result = subprocess.run(args + columns + table + where + search_string + orderby, shell=True, capture_output=True, text=True)
            oresult = result.stdout

            print(args + columns + table + where + search_string + orderby, "\n\n", oresult)


            self._tablefy(result, columns.replace("[", "").replace("]", "").split(","), [10,10,5,5,8,0,10,10,7,7,7,7,10] )
            
            
            #self.mode not self.mode
            if self.mode > 0 or self.mode < -1 :
                self.mode = -1
            else:
                self.mode = -2

            
        else:
            ###Service order Detail###
            
            print('SO#', self2)

            selected = self.results.options[self.results.value-1]
            print(selected)
            stringer = "'" + (payload or selected[0][1]) + "%'"

            columns = "[SO#],[SOSEQ#],[SOTYPE],[SOUSER],[SOMTWP],[SOMSEC],[SOMQSC],[SOMSUB],[SOMLOT],[SOMAPT],[SOSUB#],[SOPOL#],[SOPOLP],[SOBY]"
            
            args5 = 'X:\\Engineering\\GIS\\SOFTWARE\\trdsql_v0.7.6_windows_amd64\\trdsql.exe -ih  -oh -omd "select ' + columns + ' from X:\Engineering\GIS\AS400\BS400_db\SOPSOMST.csv where [SO#] like ' + stringer + ' limit 1' #+ ' order by [Pole#], [W.o.#]'

            print(args5)
            result = subprocess.run(args5, shell=True, capture_output=True, text=True)
            oresult = result.stdout

            def _so_comments_pop(self3):
                #Local function that displays the comments for a service order if the user selects it ( See SO popup below)
                print('inside', self3, self._screen)
                if self3 == 1:
                    columns = "[SO#],[SOSEQ#],[COMMENT],[SOUSER],[SOMTWP]"
                    
                    args5 = 'X:\\Engineering\\GIS\\SOFTWARE\\trdsql_v0.7.6_windows_amd64\\trdsql.exe -ih  -oh -omd "select * from X:\Engineering\GIS\AS400\BS400_db\SOPSDET.TXT where col1 like ' + stringer + ' ' #+ ' order by [Pole#], [W.o.#]'
                    args5 = 'X:\\Engineering\\GIS\\SOFTWARE\\trdsql_v0.7.6_windows_amd64\\trdsql.exe -id "\t" -oh -oat "select c1 as SO, c3 as Note from X:\Engineering\GIS\AS400\BS400_db\SOPSODET.TXT where c1 like' + stringer
                    result = subprocess.run(args5, shell=True, capture_output=True, text=True)
                    oresult = 'test'
                    oresult = result.stdout
                    print('ran something', oresult, ':', stringer)
                    #SO Comments popup
                    self._scene.add_effect(
                    PopUpDialog(screen=self._screen
                              , text=oresult
                              , buttons =['Back']
                              , has_shadow = True
                                #, on_close = self._set_so_records
                                #, on_close = _so_comments_pop
                            ))
                
            self._scene.add_effect(

            #SO popup
            PopUpDialog(screen=self._screen
                      #, [('Go To Work Order', self._on_pole_change), ('Go to Pole Detail', self._on_pole_change)]
                      , text=oresult
                      , buttons =['Back', 'SO Notes']
                      #, round(self.screen.width/2)
                      #,  round(self.screen.height/2)
                      , has_shadow = True
                        #, on_close = self._set_so_records
                        , on_close = _so_comments_pop
                    )
            )

          

         
                    
    def _on_search(self,args = 'X:\\Engineering\\GIS\\SOFTWARE\\trdsql_v0.7.6_windows_amd64\\trdsql.exe -ih -id "\t" -ocsv "select '
                   #,columns = "[Pole#], [W.o.#],[Id],[Prfx],[PLength],[Units], [Span],[No.Wires],[WSize], [WType], [Pri/sec], [CloseoutDate]  "
                   , columns = " [GPOLE#], [GPREFX],[GYEAR],[GPCOD],[GLENTH],[GSPAN],[GWIRE],[GPSIZE], [GTYPE], [GSSPAN],[GSWIRE], [GSSIZE], [GSTYPE] , (Select [GQTY1] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON1 ) || Coalesce((Select ' ' || [GQTY2] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON2 and [GQTY2] > 0 ),'') || Coalesce((Select ' ' || [GQTY3] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON3 and [GQTY3] > 0 ),'') || Coalesce((Select ' ' || [GQTY4] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON4 and [GQTY4] > 0 ),'') || Coalesce((Select ' ' || [GQTY5] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON5 and [GQTY5] > 0 ), '') || Coalesce((Select ' ' || [GQTY6] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON6 and [GQTY6] > 0 ), '') || Coalesce((Select ' ' || [GQTY7] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON7 and [GQTY7] > 0 ), '') || Coalesce((Select ' ' || [GQTY8] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON8 and [GQTY8] > 0 ), '') || Coalesce((Select ' ' || [GQTY9] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON9 and [GQTY9] > 0 ), '') || Coalesce((Select ' ' || [GQTY10] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON10 and [GQTY10] > 0 ), '') || Coalesce((Select ' ' || [GQTY11] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON11 and [GQTY11] > 0 ), '') || Coalesce((Select ' ' || [GQTY12] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON12 and [GQTY12] > 0 ),'') || Coalesce((Select ' ' || [GQTY13] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON13 and [GQTY13] > 0 ),'') || Coalesce((Select ' ' || [GQTY14] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON14 and [GQTY14] > 0 ),'') || Coalesce((Select ' ' || [GQTY15] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON15 and [GQTY15] > 0 ), '') || Coalesce((Select ' ' || [GQTY16] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON16 and [GQTY16] > 0 ), '') || Coalesce((Select ' ' || [GQTY17] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON17 and [GQTY17] > 0 ), '') || Coalesce((Select ' ' || [GQTY18] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON18 and [GQTY18] > 0 ), '') || Coalesce((Select ' ' || [GQTY19] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON19 and [GQTY19] > 0 ), '') || Coalesce((Select ' ' || [GQTY20] || 'x' || [CCONU#] as au from X:\Engineering\GIS\AS400\BS400_db\MXPCUMST_hdr.TXT where [CBINRY] like p.GCON20 and [GQTY20] > 0 ), '') as  AssemblyUnits  "
                   #, table = ' from X:\Engineering\GIS\AS400\BS400_db\MXPCPR_hdr.TXT '
                   ,table = ' from X:\Engineering\GIS\AS400\BS400_db\POPOLEMS_hdr.TXT p'
                   , where = ' where [GPOLE#] like '
                   , search_string = None
                   , orderby  = None
                   ):

        try:
            search_string = search_string or str(int(self.pole_search.value))
            search_string = "'" + search_string  +"%'"
        except:
            search_string = search_string or self.pole_search.value
            search_string = "'" + search_string  +"%'"

        orderby = orderby or ' order by cast([GPole#]as int)'
        stringer = "'"+search_string +"%'" 
       

##        columns = "[Pole#],[MapTS],[MapSec], [W.o.#],[Prfx],[PoleCode],[PLength],[Units],[Span],[No.Wires],[WSize],[WType],[Pri/sec],[CloseoutDate] "
##        columns = "[Pole#], [W.o.#],[Prfx],[PoleCode],[PLength],[Units] "
##        args5 = 'X:\\Engineering\\GIS\\SOFTWARE\\trdsql_v0.7.6_windows_amd64\\trdsql.exe -ih -id "\t"  -oh -ocsv "select ' + columns + ' from X:\Engineering\GIS\AS400\BS400_db\MXPCPR_hdr.TXT where [Pole#] like ' + stringer + ' order by cast([Pole#]as int), [W.o.#]'
        args5 = args + columns + table +where + search_string + orderby
        result = subprocess.run(args5, shell=True, capture_output=True, text=True)
        print(result)
        self._tablefy(result)


        

    def _tablefy(self
             , result
             , titles = ['GPOLE#', 'GPREFX','GYEAR','GPCOD','GLENTH','GSPAN','GWIRE','GPSIZE', 'GTYPE', 'GSSPAN', 'GSWIRE', 'GSSIZE', 'GSTYPE', 'Units']
             , columns =[10,7,7,7,8,7,10,10,10,10,10,10,7,0]
             ):      
        #Turn result into a list  based on newline category
        result = str(result.stdout).split("\n")

        #Turn result into a list of lists based on comma separated value.
        x = 0
        res = []
        for x in range(len(result)):
            a = result[x].split(',')
            result[x] = a
            res.append((a,x+1))            

        #Update the table
        self.old_results = self.results.options
        self.results = MultiColumnListBox(
                            height=self.table_height,
                 #titles =['Pole#','W.o.#', 'Id','Prfx','PLength','Units','Span','No.Wires','WSize','WType','Pri/sec','CloseoutDate'],
                            titles = titles, #titles['GPOLE#', 'GPREFX','GYEAR','GPCOD','GLENTH','GSPAN','GWIRE','GPSIZE', 'GTYPE', 'GSWIRE', 'GSSIZE', 'GSTYPE', 'Units'],
                          #columns=[10,10,5,5,8,0,10,10,10,10,10,7,10],
                            columns=columns, #[10,7,7,7,8,7,10,10,10,10,10,7,0],
                              options=[([], 1),(['Select', 'a row to ', 'See', 'a','detail', 'menu.  Large Results will scroll'], 2)],
                          label = 'Results',
                          name = 'Table',
                            add_scroll_bar = True,
                            on_change = self._on_change_upd,
                          on_select = self._on_select_pop
                            )

        #This might be a hack.  I couldn't get the table to 'reset' correctly so I just clear layout1 and create a nwe table.
        self.layout1.clear_widgets()
        self.layout1.add_widget(self.results,1)
        self.fix()
        self.save()        
        self.results.options = res

        
    def _on_change_upd(self):
        pass
    def _on_select_pop(self):
        selected = self.results.options[self.results.value-1]
        try:
            stringer = "'" + selected[0][1] + "%'"
        except:
            #If we've selected an index out of range just return.
            return
        print(selected)
        text = "Entry: " + str(selected[1]) + "\n" + "=======================================================================================\n"
        
        for x in selected[0]:
            text = text + x + " | "
            
        #if self.mode:
        if self.mode > 0:
            #text = selected[0][1]
            #button = ['Back to Search Results', 'List Poles Under SO# '+ selected[0][1],'View SO# '+selected[0][1]]
            button = ['Back to Search Results', 'List Actions for Pole# '+ selected[0][0]]
        elif self.mode < -1:
            button = ['Back to Search Results', 'List Actions for Pole# '+ selected[0][0],'View SO# '+selected[0][1]]
        else:
            #text = selected[0][0]
            #button = ['Back to Search Results', 'List Actions for Pole# '+ selected[0][0],'View SO# '+selected[0][1]]
            button = ['Back to Search Results', 'List Poles Under SO# '+ selected[0][1],'View SO# '+selected[0][1]]
        self._scene.add_effect(
            PopUpDialog(screen=self._screen
                      #, [('Go To Work Order', self._on_pole_change), ('Go to Pole Detail', self._on_pole_change)]
                      , text=text
                      , buttons =button
                      #, round(self.screen.width/2)
                      #,  round(self.screen.height/2)
                      , has_shadow = True
                        , on_close = self._control_recs
                    )
            )
        

    def _on_pole_change(self):
        self.save()
                    

    def _on_change(self):
        changed = False
        self.save()
        for key, value in self.data.items():
            if key not in form_data or form_data[key] != value:
                changed = True
                break
        self._reset_button.disabled = not changed

    
    def _reset(self):
        self.reset()
        raise NextScene()

    def _view(self):
        # Build result of this form and display it.
        try:
            self.save(validate=True)
            message = "Values entered are:\n\n"
            for key, value in self.data.items():
                message += "- {}: {}\n".format(key, value)
        except InvalidFields as exc:
            message = "The following fields are invalid:\n\n"
            for field in exc.fields:
                message += "- {}\n".format(field)
        self._scene.add_effect(
            PopUpDialog(self._screen, message, ["OK"]))

    def _quit(self):
        self._scene.add_effect(
            PopUpDialog(self._screen,
                        "Are you sure?",
                        ["Yes", "No"],
                        has_shadow=True,
                        on_close=self._quit_on_yes))

    @staticmethod
    def _action_menu(selected):
        print("Action", selected)

        

    @staticmethod
    def _check_email(value):
        m = re.match(r"^[a-zA-Z0-9_\-.]+@[a-zA-Z0-9_\-.]+\.[a-zA-Z0-9_\-.]+$",
                     value)
        return len(value) == 0 or m is not None

    @staticmethod
    def _quit_on_yes(selected):
        # Yes is the first button
        if selected == 0:
            raise StopApplication("User requested exit")


def demo(screen, scene):
    screen.set_title('BS400')
    screen.play([Scene([
        Background(screen),
        DemoFrame(screen)
    ], -1)], stop_on_resize=True, start_scene=scene, allow_int=True)


last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
        os.system("mode con cols=175")


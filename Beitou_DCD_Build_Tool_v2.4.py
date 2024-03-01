"""
1.XML的大体框架已经构造出来
2.将build DCD 与 Build XML 两个功能做在一起
3.2023-1-1 版本号为1.0.0.0 edit ben
4.2023-1-3 版本号为1.0.0.1
  1.修正进度条 当运行FAIL的时候 进度条应该变红
  2.修正程式部分不合理部分
  3.增加反馈机制
  4.修改discard 功能按钮
  5.增加umount按钮功能
  6.修正一些可能的报错信息，尽可能让错误信息停下来
5.2023-2-21 修正部分按钮的名称和按钮
6.2023/2/28
  1.利用copy的深拷贝将变量进行赋值
7.2023/3/6
  1.Beitou_DCD_Bild_tool 2.0版本发布
8.2023/3/15 2.1
    1.修正删除参数RD /s /q \\\? 避免了删除绝对路径过长的而导致路径不对的情况发生
    2.增加报错时信息的显示
    3.修正进度条显示异常的问题

9.2023/3/18 2.2
    1.修正mount DCD 权限不够导致的进度条报错信息不准确的情况发生
    2.修正只更新inst.ini 文件时 driver CD name 没有更新的情况
    3.增加build DCD PASS提示信息
    4.优化程式结构，加速运行速度
    5.修正程式测报错机制和退出机制
10.2023/3/18 2.3
    1.修正判断inst.ini 因为版本去判断是否决定更换组件的逻辑
    2.增加umount 功能按钮（commit/discard）的选项
    3.check file 页面修复部分逻辑和页面调整
11.2023/11/14 2.4
    1.修正当驱动文件包里面里面有两个驱动时候，暂用了两个驱动包，增加提示信息
    2.修改文件的版本
    3.3.0.0.3
"""


import datetime
import time
# import pathlib
# from queue import Queue
import tkinter.messagebox
# import tkinter.simpledialog
from tkinter import END
from threading import Thread
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
from tkinter.scrolledtext import ScrolledText
from ttkbootstrap.dialogs import Messagebox
from threading import Thread

import xml.dom.minidom
import os
import sys

import chardet
import re

import json
import subprocess
import traceback
import shutil
from shutil import copyfile
from xml.dom.minidom import parse
import hashlib
import copy


class Buildxmlfile(ttk.Frame):

    # queue = Queue()
    # searching = False

    def __init__(self, master):
        super().__init__(master, padding=15, )  # 继承的容器 内边距为15 这个master 就是root
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.master.geometry(
            f"{int(self.screen_width / 1.3)}x{int(self.screen_height / 1.3)}+{int(self.screen_width / 6)}+{int(self.screen_height / 8)}")  # 设置窗口属性 确定
        self.pack(fill=BOTH, expand=YES)  # 在容器的位置，fill 决定是否拉升，expand 在窗口拖放时是否决定拖放

        self.tab_main = ttk.Notebook(self, bootstyle="secondary")  # 创建分页栏bootstyle="success"
        self.tab_main.pack(fill=BOTH, expand=False, anchor=N, side=TOP)

        self.xml = ttk.Frame(self.tab_main,)
        self.xml.pack(fill=X, expand=False, anchor=N, side=TOP)  # 如果容器的改变 空间变大的时候，该容器会变大

        self.build_dcd = ttk.Frame(self.tab_main,)
        self.build_dcd.pack(fill=X, expand=False, anchor=N, side=TOP)  # 如果容器的改变 空间变大的时候，该容器会变大

        self.check_file = ttk.Frame(self.tab_main,)
        self.check_file.pack(fill=X, expand=False, anchor=N, side=TOP)  # 如果容器的改变 空间变大的时候，该容器会变大

        self.tab_main.add(self.build_dcd, text='Build DCD')  # 将第一页插入分页栏中
        self.tab_main.add(self.xml, text='Build XML',)  # 将第一页插入分页栏中
        self.tab_main.add(self.check_file, text='Check File', )  # 将第一页插入分页栏中
        # self.tab_main.add(self.build_dcd, text='Build DCD File',)  # 将第一页插入分页栏中

        self.py_path = os.getcwd()
        # 这是for num 3页面进行调试
        self.remark_location = True







        # ================================================================================================================
        # ========================================================第二页===================================================
        # ================================================================================================================
        self.driver_name = ttk.StringVar(value="")
        self.path_var_inst = ttk.StringVar(value="")
        self.path_var_driver = ttk.StringVar(value="")
        self.path_var_comment = ttk.StringVar(value="")
        self.xml_name = ttk.StringVar(value='')
        self.path_var_DCD = ttk.StringVar(value="")
        self.path_var_XML = ttk.StringVar(value="")
        self.progressbar_dcd_text_value = ttk.StringVar(value="0%")
        self.output_file_pass = ""
        # ================================================================================================================
        # 标题

        self.option_lf1 = ttk.Frame(self.xml, padding=15, )  # 创建一个线边框的容器 古挂载在ttk.Frame 容器上面
        self.option_lf1.pack(fill=X, expand=False, anchor=N, side=TOP)  # 如果容器的改变 空间变大的时候，该容器会变大
        # option_title_text = "Build XML File"
        # path_lbl2 = ttk.Label(self.option_lf1, text=option_title_text, padding=2, bootstyle="success",
        #                       font=("微软雅黑", 20), anchor=CENTER, )  # 在新创建的窗口容器上加上一个label 标签，内容是path  宽是8个像素
        # path_lbl2.pack(side=TOP, pady=(0, 0), anchor=N, fill=X,
        #                expand=YES)  # 挂载方式是在容器的左边 并且 padx=(0, 15) padx 是与外接组件的边距（左右）两个值

        self.style = ttk.Style()
        # ================================================================================================================
        option_text = "信息确认区域"
        self.option_lf = ttk.Labelframe(self.xml, text=option_text, padding=15, bootstyle="light"
                                       )  # 创建一个线边框的容器 古挂载在ttk.Frame 容器上面
        self.option_lf.pack(fill=BOTH, expand=YES, anchor=CENTER,side=TOP,pady=20 )  # 如果容器的改变 空间变大的时候，该容器会变大


        # 创建一个输入框 输出需要更改的DCD的名字的值
        self.path_row = ttk.Frame(self.option_lf)  # 在 线边框的容器中继续放入创建一个容器
        self.path_row.pack(fill=X, expand=YES, pady=10)  # 挂载的方式 是相对路径的pack X方向平铺，并且随着窗口扩展
        label_tame = "键入DCD Name:"
        self.driver_name_label = ttk.Label(self.path_row, text=label_tame, bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.path_ent = ttk.Entry(self.path_row, textvariable=self.driver_name)
        self.path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5,)

        self.path_row1 = ttk.Frame(self.option_lf)  # 在 线边框的容器中继续放入创建一个容器
        self.path_row1.pack(fill=X, expand=YES, pady=10)  # 挂载的方式 是相对路径的pack X方向平铺，并且随着窗口扩展
        label_tame = "键入XML Name:"
        self.driver_name_label = ttk.Label(self.path_row1, text=label_tame,  bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.path_ent1 = ttk.Entry(self.path_row1, textvariable=self.xml_name)
        self.path_ent1.pack(side=LEFT, fill=X, expand=YES, padx=5, )
        # browse_btn = ttk.Button(
        #     master=self.path_row,
        #     text="Start",
        #     command=self.on_browse1,
        #     width=8
        # )
        # browse_btn.pack(side=LEFT, padx=5)
        # self.driver_name.set('input your text here')

        # 选择inst.ini的文件复选框
        self.term_row = ttk.Frame(self.option_lf)
        self.term_row.pack(fill=X, expand=YES, pady=15)
        label_tame = "选择Inst.ini文件:"
        self.driver_name_label = ttk.Label(self.term_row, text=label_tame, bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.path_ent_inst = ttk.Entry(self.term_row, textvariable=self.path_var_inst)
        self.path_ent_inst.pack(side=LEFT, fill=X, expand=YES, padx=5, )
        browse_btn = ttk.Button(
            master=self.term_row,
            text="Browse",
            command=self.on_browse1,
            width=8,
            bootstyle="success"
        )
        browse_btn.pack(side=LEFT, padx=5)

        # 确定一个驱动文件文件包的
        self.driver_row = ttk.Frame(self.option_lf)
        self.driver_row.pack(fill=X, expand=YES, pady=15)
        label_tame = "选择驱动安装包:"
        self.driver_name_label = ttk.Label(self.driver_row, text=label_tame,  bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.path_ent_driver = ttk.Entry(self.driver_row, textvariable=self.path_var_driver)
        self.path_ent_driver.pack(side=LEFT, fill=X, expand=YES, padx=5, )
        browse_btn = ttk.Button(
            master=self.driver_row,
            text="Browse",
            command=self.on_browse2,
            width=8,
            bootstyle="success"
        )
        browse_btn.pack(side=LEFT, padx=5)

        # 确定是否有新增加的组件
        self.comment_row = ttk.Frame(self.option_lf)
        self.comment_row.pack(fill=X, expand=YES, pady=15)
        label_tame = "增加Stage组件: "
        self.driver_name_label = ttk.Label(self.comment_row, text=label_tame,  bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.path_ent_Stage = ttk.Entry(self.comment_row, textvariable=self.path_var_comment)
        self.path_ent_Stage.pack(side=LEFT, fill=X, expand=YES, padx=5, )
        browse_btn = ttk.Button(
            master=self.comment_row,
            text="Browse",
            command=self.on_browse3,
            width=8,
            bootstyle="success"
        )
        browse_btn.pack(side=LEFT, padx=5)

        self.start_row = ttk.Frame(self.option_lf)
        self.start_row.pack(fill=X, expand=YES, pady=15)
        browse_btn = ttk.Button(
            master=self.start_row,
            text="Start Build XML",
            command=self.on_browse4,
            width=20,
            bootstyle="danger"
        )
        browse_btn.pack(anchor=CENTER, padx=5)

        # self.text_frame = ttk.Frame(self.xml)
        # self.text_frame.pack(fill=X, expand=YES, pady=15)
        option_text = "程式运行信息"
        self.text_frame = ttk.Labelframe(self.xml, text=option_text, padding=15,bootstyle="light"
                                        )  # 创建一个线边框的容器 古挂载在ttk.Frame 容器上面
        self.text_frame.pack(fill=BOTH, expand=YES, anchor=N, side=TOP)  # 如果容器的改变 空间变大的时候，该容器会变大
        self.textbox = ScrolledText(
            master=self.text_frame,
            highlightcolor=self.style.colors.primary,
            highlightbackground=self.style.colors.border,
            highlightthickness=1
        )
        self.textbox.pack(fill=X,expand=YES, anchor=N, side=TOP)


        # self.progressbar = ttk.Progressbar(self.xml, name="proless", length=self.screen_width / 1.5,
        #                                    bootstyle="Success-striped", phase=False)
        # self.progressbar.pack(fill=BOTH, expand=YES, anchor=N, side=BOTTOM, pady=3)
        # self.progressbar["maximum"] = 5

        # ================================================================================================================
        # ========================================================第二页===================================================
        # ================================================================================================================
        # self.build_dcd
        option_text = "信息确认区域"
        self.option_lf_DCD = ttk.Labelframe(self.build_dcd, text=option_text, padding=15,
                                            bootstyle="light")  # 创建一个线边框的容器 古挂载在ttk.Frame 容器上面
        self.option_lf_DCD.pack(fill=BOTH, expand=YES, anchor=CENTER,side=TOP )  # 如果容器的改变 空间变大的时候，该容器会变大
        self.driver_row = ttk.Frame(self.option_lf_DCD)
        self.driver_row.pack(fill=X, expand=YES, pady=15)
        label_tame = "选择DCD文件:   "
        self.driver_name_label = ttk.Label(self.driver_row, text=label_tame, bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.path_ent_dcd = ttk.Entry(self.driver_row, textvariable=self.path_var_DCD, )
        self.path_ent_dcd.pack(side=LEFT, fill=X, expand=YES, padx=5, )
        browse_btn = ttk.Button(
            master=self.driver_row,
            text="Browse",
            command=self.on_browse6,
            width=8,
            bootstyle="success"
        )
        browse_btn.pack(side=LEFT, padx=5)

        # 选择XML的文件
        self.driver_row = ttk.Frame(self.option_lf_DCD)
        self.driver_row.pack(fill=X, expand=YES, pady=15)
        label_tame = "选择XML文件:   "
        self.driver_name_label = ttk.Label(self.driver_row, text=label_tame, bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.path_ent_xml = ttk.Entry(self.driver_row, textvariable=self.path_var_XML)
        self.path_ent_xml.pack(side=LEFT, fill=X, expand=YES, padx=5, )
        browse_btn = ttk.Button(
            master=self.driver_row,
            text="Browse",
            command=self.on_browse5,
            width=8,
            bootstyle="success"
        )
        browse_btn.pack(side=LEFT, padx=5)

        self.start_row = ttk.Frame(self.option_lf_DCD)
        self.start_row.pack(fill=X, expand=YES, pady=15)

        browse_btn = ttk.Button(
            master=self.start_row,
            text="Umount DCD",
            command=self.on_browse8,
            width=20,
            bootstyle="danger"

        )
        browse_btn.pack(anchor=CENTER, padx=10, side=LEFT)

        # 增加一个参数选项
        self.vproduct = ttk.StringVar(value="discard")
        self.theme_cbo2 = ttk.Combobox(
            master=self.start_row,
            font=("微软雅黑", 10),
            cursor="arrow",
            textvariable=self.vproduct,
            state="readonly",
            bootstyle="success",
            width=7)
        self.theme_cbo2.pack(anchor=CENTER, padx=20, side=LEFT)
        self.theme_cbo2["values"] = ["discard", "commit"]

        browse_btn = ttk.Button(
            master=self.start_row,
            text="Build DCD",
            command=self.on_browse7,
            width=20,
            bootstyle="danger"
        )
        browse_btn.pack(side=LEFT, padx=300, anchor=CENTER)

        browse_btn = ttk.Button(
            master=self.start_row,
            text="Mount DCD",
            command=self.on_browse9,
            width=20,
            bootstyle="danger"

        )
        browse_btn.pack(side=LEFT, padx=50, anchor=CENTER)

        # self.text_frame = ttk.Frame(self.xml)
        # self.text_frame.pack(fill=X, expand=YES, pady=15)
        option_text = "程式运行信息"
        self.text_frame = ttk.Labelframe(self.build_dcd, text=option_text, padding=15, bootstyle="light"
                                         )  # 创建一个线边框的容器 古挂载在ttk.Frame 容器上面
        self.text_frame.pack(fill=BOTH, expand=YES, anchor=CENTER, side=TOP)  # 如果容器的改变 空间变大的时候，该容器会变大
        self.textbox_dcd = ScrolledText(
            master=self.text_frame,
            highlightcolor=self.style.colors.primary,
            highlightbackground=self.style.colors.border,
            highlightthickness=1,
            # bg='red'

        )
        self.textbox_dcd.pack(fill=BOTH, expand=YES, anchor=N, side=TOP,pady=10)

        # option_text = "程式运行进程"
        # self.text_frame1 = ttk.Labelframe(self.build_dcd, text=option_text, padding=15, bootstyle="light"
        #                                   )  # 创建一个线边框的容器 古挂载在ttk.Frame 容器上面
        # self.text_frame1.pack(fill=X, expand=YES, anchor=N, side=TOP)  # 如果容器的改变 空间变大的时候，该容器会变大

        self.progressbar_dcd = ttk.Progressbar(self.text_frame, name="proless", length=self.screen_width / 1.5,
                                               bootstyle="Success-striped", phase=False)
        self.progressbar_dcd.pack(fill=X, expand=YES, anchor=CENTER, side=BOTTOM,)
        self.progressbar_dcd["maximum"] = 10
        self.progressbar_dcd_text = ttk.Label(self.progressbar_dcd, textvariable=self.progressbar_dcd_text_value,bootstyle="default").pack()
        # self.progressbar_dcd_text.config(text="NA", bootstyle=(SUCCESS, INVERSE))

        # ================================================================================================================
        # ========================================================第三页===================================================
        # ================================================================================================================
        # self.check_file
        option_text = "组件包信息确认"
        self.check_driver_file = ttk.Labelframe(self.check_file, text=option_text, padding=15,
                                            bootstyle="light")  # 创建一个线边框的容器 古挂载在ttk.Frame
        self.check_driver_file.pack(fill=X, expand=YES, anchor=N, )  # 如果容器的改变 空间变大的时候，该容器会变大

        # option_text = "组件包规范检查"
        # self.check_driver_file1 = ttk.Labelframe(self.check_file, text=option_text, padding=15,
        #                                         bootstyle="light")  # 创建一个线边框的容器 古挂载在ttk.Frame 容器上面
        # self.check_driver_file1.pack(fill=X, expand=YES, anchor=N, )  # 如果容器的改变 空间变大的时候，该容器会变大
        # 增一个页面来装一些功能选项
        self.check_driver_row = ttk.Frame(self.check_driver_file)
        self.check_driver_row.pack(fill=X, expand=YES, pady=15)



        # 选择驱动安装的选项
        label_tame = "选择驱动安装包:"
        self.driver_name_label = ttk.Label(self.check_driver_row, text=label_tame, bootstyle="success")
        self.driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.check_path_ent_driver = ttk.Entry(self.check_driver_row, textvariable=self.path_var_driver)
        self.check_path_ent_driver.pack(side=LEFT, fill=X, expand=YES, padx=5, )
        browse_btn = ttk.Button(
            master=self.check_driver_row,
            text="Browse",
            command=self.on_browse2,
            width=8,
            bootstyle="success"
        )
        browse_btn.pack(side=LEFT, padx=5)

        # 选择检测的inst.ini 文档
        # 选择inst.ini的文件复选框
        self.check_term_row = ttk.Frame(self.check_driver_file)
        self.check_term_row.pack(fill=X, expand=YES, pady=15)
        label_tame = "选择Inst.ini文件:"
        self.check_driver_name_label = ttk.Label(self.check_term_row, text=label_tame, bootstyle="success")
        self.check_driver_name_label.pack(side=LEFT, padx=(15, 0))
        self.check_path_ent_inst = ttk.Entry(self.check_term_row, textvariable=self.path_var_inst)
        self.check_path_ent_inst.pack(side=LEFT, fill=X, expand=YES, padx=5, )


        browse_btn = ttk.Button(
            master=self.check_term_row,
            text="Browse",
            command=self.on_browse1,
            width=8,
            bootstyle="success"
        )
        browse_btn.pack(side=LEFT, padx=5)


        self.check_Sep = ttk.Separator(self.check_driver_file,bootstyle="success")
        self.check_Sep.pack(fill=X, expand=YES, padx=5, pady=5)

        self.check_butt = ttk.Frame(self.check_driver_file)
        self.check_butt.pack(fill=X, expand=YES, pady=15, side=TOP)

        self.browse_btn_start = ttk.Button(
            master=self.check_butt,
            text="开始检测",
            command=self.start_check,
            width=20,
            bootstyle="danger"
        )
        self.browse_btn_start.pack(side=LEFT, anchor=CENTER, padx=400, pady=10)
        browse_btn_out = ttk.Button(
            master=self.check_butt,
            text="导出文件",
            command=self.out_put_jion_file,
            width=20,
            bootstyle="danger"
        )
        browse_btn_out.pack(side=LEFT, anchor=CENTER, padx=5, pady=10)

        self.check_butt_list = ttk.Frame(self.check_driver_file)
        self.check_butt_list.pack(fill=X, expand=YES, pady=15, side=TOP)
        self.check_driver_row1 = ttk.Frame(self.check_driver_file)
        self.check_driver_row1.pack(fill=X, expand=YES, pady=15, anchor=N, side=TOP)
        tile_list = ["序数", "组件包", "组件类型", "Stage 编号", "组件版本号", "版本修正", "检测结果"]
        for i in tile_list:
            self.driver_name_label = ttk.Button(
                master=self.check_butt_list,
                cursor="arrow",
                text=i,
                state="readonly",
                bootstyle="success-outline",
                width=17,
            )
            self.driver_name_label.pack(side=LEFT, fill=X, expand=YES, padx=5, anchor=N)
        # self.check_driver_row2 = ttk.Frame(self.check_file)
        # self.check_driver_row2.pack(fill=X, expand=YES, pady=15, side=TOP)
        self.check_Sep = ttk.Separator(self.check_driver_row1, bootstyle="success")
        self.check_Sep.pack(fill=X, expand=YES, padx=5, pady=5, side=TOP)

    def switchtojson(self,date):
        driver_path = self.check_path_ent_driver.get().strip(" ").strip("\n")
        os.chdir(driver_path)
        date = [date]
        new_data = json.dumps(date)
        with open("file.json", "w", encoding="utf-16") as fp:
            # dump 将JSON 的字符串类型的输出到一个JSON文件里面
            json.dump(new_data, fp, ensure_ascii=True)
        if os.path.exists("file.json"):
            return "file.json"
        else:
            return False

    # 将JSON 文件转换成 python格式字符串
    def switchtoPy(self,date):
        read_type = self.check_file_type(date)
        if read_type:
            with open(f"{date}", encoding=f"{read_type}") as fp:
                lists = json.load(fp)
            datas = json.loads(lists)
            # 将这种格式的[{}]的文档进行转换
            datas = datas[0]
            if datas:
                return datas
            else:
                return False

    def out_put_jion_file(self):
        # 这里需要假日一个标志位 用于接收
        # 改变标志位
        # 该函数需要检查是否还是有NA的情况发生，但是应该是检查 就怕有个坑壁误操作
        # 着手闯将json 的文件的生成和读写

        if self.output_file_pass:
            self.check_item = "PASS"
            for key, value in self.output_file_pass.items():
                if self.check_item == "PASS":
                    for k, v in value.items():
                        if k.find("NA") != -1:
                            print(f"-{k}-")
                            Messagebox.show_error(f"组件{key}的stage有问题待确认",title="组件包ERROR")
                            self.check_item = "FAIL"
                            break
                        else:
                            for i in v:
                                if i.find("NA") != -1 or i.find(" ") != -1:
                                    Messagebox.show_error(f"组件{key}的version有问题待确认", title="组件包ERROR")
                                    self.check_item = "FAIL"
                                    break
                else:
                    Messagebox.show_error(f"组件{key}的version有问题待确认", title="组件包ERROR")
                    break
        if self.check_item != "FAIL":
            # 这里创建json的文档输出
            """
                {'05.Intel_Graphics_31.0.101.3887': {'[Stage 74]': ['Driver', '31.0.101.3887']}, 
                '1.ddddddd': {'[Stage 88]': ['Driver', '2.3.4.5']}, 
                '11.RTK_Codec_6.0.9445.1': {'[Stage 82]': ['Driver', '6.0.9445.1']}, 
                '11_1.Rtk_Audio_UWP_1.40.286.0': {'[Stage 158]': ['StoreAPP', '1.40.286.0']}, 
                '12.Dolby_APO_7.1128.706.52': {'[Stage 102]': ['Driver', '7.1128.706.52']}, 
                '12_1.Dolby_UWP_3.15.694.0': {'[Stage 106]': ['StoreAPP', '3.15.694.0']}, 
                '16.NVIDIA_GFX_31.0.15.2717': {'[Stage 76]': ['Driver', '31.0.15.2717']}, 
                '18.Numberpad_17.0.0.13': {'[Stage 98]': ['Driver', '17.0.0.13']}, 
                '19.Morpho_AI_Camera_1.0.4.5': {'[Stage 148]': ['Driver', '1.0.4.5']}
                }
            """
            self.remark_location = False
            file =  self.switchtojson(self.output_file_pass)
            if file:
                self.browse_btn_start.configure(state="disabled")
                Messagebox.show_info("组件包确认完成,已生成file.json文档", title="PASS")
            else:
                Messagebox.show_error("组件包未确认PASS,已生成file.json文档", title="ERROR")
            print(self.output_file_pass)

        else:
            Messagebox.show_info("组件未完成", title="ERROR")


    def start_check(self):
        drive_coment = self.check_path_ent_driver.get().strip(" ").strip("\n")
        inst_file = self.check_path_ent_inst.get().strip(" ").strip("\n")
        if not drive_coment and not inst_file:
            Messagebox.show_error("没有确认组件包和inst.ini文件",title="ERROR")
        def start_chk():

            drive_coment = self.check_path_ent_driver.get().strip(" ").strip("\n")
            inst_file = self.check_path_ent_inst.get().strip(" ").strip("\n")
            if drive_coment and inst_file:
                inst_dict = self.getinstinfo(inst_file)
                # print(inst_dict)
                file_list = os.listdir(drive_coment)
                drive_coment_dis = []
                for i in file_list:
                    # 判断是否为文件
                    if os.path.isdir(f"{drive_coment}\\{i}"):
                        drive_coment_dis.append(i)
                if len(drive_coment_dis) != 0:
                    print("ff")
                    #创建fail和pass的两个集合,fail和PASS的分界线就是在inst.ini有无找到stage的标识符号
                    # 如果FAIL的应该还要考虑将包的文件名字进行更改
                    # 1.创建一个收集PASS 集合
                    self.check_it_pass = {}
                    #2.创建一个收集Fail 的集合
                    check_it_fail = {}
                    for driver_name in drive_coment_dis:
                        # 这是符合规范的驱动包的命令规范
                        ck = "(^\d.*\d$)"
                        if re.findall(ck, driver_name):
                            # print(driver_name)
                            # 确定的名字的规范后 看是否在inst.ini
                            ck1 = r"[-_]"
                            # 这是应对那种11_1 这种坑壁的设计
                            if re.findall("(^\d?\d$)",re.split(ck1,driver_name)[0]):
                                check_driver_bao_name = "_".join(re.split(ck1,driver_name)[0:2])
                            else:
                                check_driver_bao_name = re.split(ck1,driver_name)[0]
                            # print(check_driver_bao_name)
                            check_driver_bao_version = re.split(ck1,driver_name)[-1]
                            # print(check_driver_bao_name)
                            for key, value in inst_dict.items():
                                for k, v in value.items():
                                    if v.find(check_driver_bao_name) != -1:
                                        # print(key,driver_name,check_driver_bao_version)
                                        # 这里需要文件来接收 那些OK的
                                        # print(key,check_driver_bao_name)
                                        check_driver_stype = inst_dict[key]['AsName'].split("\\")[0].strip(" ").strip("\n")
                                        self.check_it_pass[f"{driver_name}"] = {key:[check_driver_stype,check_driver_bao_version]}
                                        continue

                            # 这种情况是为了那种符合组件的规范的 但是又再inst.ini中找不到的
                            if driver_name in self.check_it_pass.keys():
                                continue
                            else:
                                check_driver_stype = "NA"
                                # check_driver_bao_version = "NA"
                                key = "NA"
                                self.check_it_pass[f"{driver_name}"] = {key: ["NA", check_driver_bao_version]}
                                # check_it_pass[f"{driver_name}"] = {"NA": check_driver_bao_version}
                        else:
                            # 不在规范里面的我们要单独在考虑,但是即使是不在规范的命名方式 我们是不是也可以将
                            # print("这个不是规范的驱动包命令方式")
                            # print(driver_name)
                            ck1 = r"[-_]"
                            check_driver_bao_name = re.split(ck1, driver_name)[0]
                            for key,value in inst_dict.items():
                                for k,v in value.items():
                                    if v.find(check_driver_bao_name) != -1:
                                        # print(key,driver_name,"NA")
                                        check_driver_stype = inst_dict[f"{key}"]["AsName"].split("\\")[0].strip(" ").strip(
                                            "\n")
                                        self.check_it_pass[f"{driver_name}"] = {key: [check_driver_stype,"NA"]}
                            if driver_name in self.check_it_pass.keys():
                                continue
                            else:
                                self.check_it_pass[f"{driver_name}"] = {"NA": ["NA","NA"]}

                    print(self.check_it_pass)
                    # 确定收录的个数与检测的个数进行比对 如果一致的话 在进行后面的动作，并且也还要保证名称是否都在
                    if len(drive_coment_dis) == len(self.check_it_pass.keys()):
                        not_in_coment = []
                        for i in drive_coment_dis:
                            if i not in self.check_it_pass.keys():
                                not_in_coment.append(i)
                        if len(not_in_coment) == 0:
                            # 开始创建表格形式的 然后填写对应的stage的版块 最后

                            count = 1

                            # self.xxx = ttk.StringVar(value="NA")
                            self.cool = ttk.StringVar(value="NA")
                            self.ver = ttk.StringVar(value="NA")

                            """
                            将driver list 前面的那些无用的版本给去掉，
                            """
                            list_stage1 = list(inst_dict.keys())
                            list_stage = list(inst_dict.keys())
                            print(list_stage)
                            remove_list = ["[OS_Language_Tag]","[ScdInst]","[Stage 601]","[FileList]","[Driver_CD","[Stage 499]"]
                            for i in list_stage1:
                                for ii in remove_list:
                                    if i.find(ii) != -1:
                                        list_stage.remove(i)


                            """
                            将之前已经被驱动包选中的stage 剔除掉
                            """
                            check_it_pass_stage = []
                            for key, value in self.check_it_pass.items():
                                for k, v in value.items():
                                    check_it_pass_stage.append(k)


                            if len(check_it_pass_stage) != 0:
                                list_stage2 = []
                                for x in list_stage:
                                    list_stage2.append(x)



                                for i in list_stage2:
                                    # print(i)
                                    for ii in check_it_pass_stage:
                                        print(i, ii)
                                        if i.find(ii) != -1:
                                            try:
                                                list_stage.remove(i)
                                            except:
                                                tkinter.messagebox.showerror(title="error", message="有有两个驱动文件重复了，占用了两个stage")
                                                sys.exit()
                                                break



                            # 接收一个被NA的参数值，用于后面重新确认分配并生成一个新的画面
                            self.check_it_faile_list = []

                            for key, value in self.check_it_pass.items():
                                for k, v in value.items():
                                    locals()[f"self.cool{key}"] = ttk.StringVar(value=v[0])
                                    locals()[f"self.ver{key}"] = ttk.StringVar(value="")
                                    # print(id(locals()[f"self.ver{key}"]))
                                    item_Frame_main = ttk.Frame(self.check_file)
                                    item_Frame_main.pack(fill=X, expand=YES, pady=15,anchor=N,side=TOP)
                                    item_Frame = ttk.Frame(item_Frame_main)
                                    item_Frame.pack(fill=X, expand=YES, pady=3,anchor=N, side=TOP)
                                    # 增加一个序列号
                                    self.driver_name_label1 = ttk.Button(item_Frame, text=f"Num {count}",
                                                                       bootstyle="warning")

                                    self.driver_name_label1.pack(side=LEFT, fill=X, padx=5)

                                    # 增加一个组件包的名字
                                    self.driver_name_label = ttk.Button(
                                        master=item_Frame,
                                        cursor="arrow",
                                        text=f"{key}",
                                        state="readonly",
                                        bootstyle="success-outline",
                                        width=17,
                                    )
                                    self.driver_name_label.pack(side=LEFT, fill=X, expand=YES, padx=5)

                                    locals()[f"self.browse_btn{key}_stpy"] = ttk.Button(
                                        master=item_Frame,
                                        cursor="arrow",
                                        text=v[0],
                                        state="readonly",
                                        bootstyle="success-outline",
                                        width=17,
                                    )
                                    locals()[f"self.browse_btn{key}_stpy"].pack(side=LEFT, fill=X, expand=YES, padx=5)

                                    if k == "NA":
                                        locals()[f"self.theme{key}"] = ttk.Combobox(
                                            master=item_Frame,
                                            font=("微软雅黑", 10),
                                            cursor="arrow",
                                            textvariable=locals()[f"self.cool{key}"],
                                            state="readonly",
                                            # bootstyle="warning",
                                            width=30)
                                        locals()[f"self.theme{key}"].pack(side=LEFT, padx=10, anchor=CENTER, fill=X, )
                                        # w我认为这里应该需要修正以下参数数据
                                        locals()[f"self.theme{key}"]["values"] = list_stage
                                        # self.check_it_faile_list.append("fail")

                                    else:
                                        locals()[f"self.browse_btn{key}"] = ttk.Button(
                                            master=item_Frame,
                                            cursor="arrow",
                                            text=k,
                                            state="readonly",
                                            bootstyle="success-outline",
                                            width=17,
                                        )
                                        locals()[f"self.browse_btn{key}"].pack(side=LEFT, fill=X, expand=YES, padx=5)

                                    # if v[1] != "NA" or:
                                    locals()[f"self.browse_ver{key}"] = ttk.Button(
                                         master=item_Frame,
                                        cursor="arrow",
                                        text=v[1],
                                        state="readonly",
                                        bootstyle="success-outline",
                                        width=17
                                    )

                                    locals()[f"self.browse_ver{key}"].pack(side=LEFT, fill=X, expand=YES, padx=5)
                                    # 将这个栏位作为version 矫正的栏位
                                    locals()[f"self.check_ver{key}"] = ttk.Entry(item_Frame, textvariable=locals()[f"self.ver{key}"], )
                                    locals()[f"self.check_ver{key}"].pack(side=LEFT, fill=X, expand=YES, padx=5,)
                                    # locals()[f"self.ver{key}"].set(value=v[1])
                                    # self.check_it_faile_list.append("fail")
                                    # self.check_it_faile_list[locals()[f"self.check_ver{key}"]] = key

                                    # 增加一个判断判断PASS和FAIl的状态
                                    if k == "NA" or v[1] == "NA":
                                        locals()[f"self.check_pass{key}"] = ttk.Button(item_Frame,bootstyle="danger",text="FAIL")
                                    else:
                                        locals()[f"self.check_pass{key}"] = ttk.Button(item_Frame,bootstyle="success",text="PASS")
                                    locals()[f"self.check_pass{key}"].pack(side=LEFT, fill=X, expand=YES, padx=5, )
                                    count = count + 1
                            else:
                                self.check_it_faile_list.append("fail")
                                if len(self.check_it_faile_list) != 0:
                                    # 这个循环要要加一个人终止判断
                                    check_item_pass = copy.deepcopy(self.check_it_pass)
                                    self.output_file_pass = self.check_it_pass
                                    # print(id(check_item_pass))
                                    # print(id(self.output_file_pass))
                                    while self.remark_location:
                                        # 将stage 为NA的情况提出来
                                        for key, value in check_item_pass.items():
                                            # time.sleep(0.5)
                                            for k, v in value.items():
                                                if v[1] == "NA" and k == "NA":
                                                    # print("111")
                                                    if locals()[f"self.theme{key}"].get().strip(" ").strip("\n") != "NA" and locals()[f"self.theme{key}"].get().strip(" ").strip("\n") != "" and locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n") != "NA" and locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n") != "":
                                                        stage_name = locals()[f"self.theme{key}"].get().strip(" ").strip("\n")
                                                        check_version = locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n")
                                                        if stage_name != "":
                                                            check_driver_stype = inst_dict[f"{stage_name}"]["AsName"].split("\\")[0].strip(" ").strip("\n")
                                                            locals()[f"self.browse_btn{key}_stpy"].configure(text=check_driver_stype)
                                                            if check_version != "":
                                                                locals()[f"self.browse_ver{key}"].configure(text=check_version)
                                                                locals()[f"self.check_pass{key}"].configure(bootstyle="success",text="PASS")
                                                            else:
                                                                locals()[f"self.browse_ver{key}"].configure(text=v[1])
                                                                locals()[f"self.check_pass{key}"].configure(bootstyle="danger", text="FAIL")
                                                            self.output_file_pass[f"{key}"] = {f"{stage_name}":[f"{check_driver_stype}",f"{check_version}"]}
                                                        else:
                                                            locals()[f"self.browse_btn{key}_stpy"].configure(text=k)
                                                            locals()[f"self.check_pass{key}"].configure(bootstyle="danger", text="FAIL")
                                                        if stage_name == "" or check_version == "" or check_version == " ":
                                                            locals()[f"self.check_pass{key}"].configure(bootstyle="danger",text="FAIL")
                                                    else:
                                                        locals()[f"self.check_pass{key}"].configure(bootstyle="danger",text="FAIL")


                                                elif k != "NA" and v[1] == "NA":
                                                    # print(locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n") != "NA")
                                                    check_version = locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n")
                                                    # print(f"uu{check_version}uu")
                                                    if check_version != "NA" and check_version != "":
                                                        locals()[f"self.browse_ver{key}"].configure(text=check_version)
                                                        # print(locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n") != "NA")
                                                        locals()[f"self.check_pass{key}"].configure(bootstyle="success", text="PASS")
                                                        self.output_file_pass[f"{key}"][f"{k}"][1] = check_version
                                                        # locals()[f"self.check_pass{key}"].configure(bootstyle="success",text="PASS")
                                                        locals()[f"self.check_pass{key}"].configure(text="PASS")
                                                        # print("222")

                                                    else:
                                                        locals()[f"self.browse_ver{key}"].configure(text=v[1])
                                                        # print(locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n") != "NA")
                                                        locals()[f"self.check_pass{key}"].configure(bootstyle="danger", text="FAIL")
                                                        locals()[f"self.check_pass{key}"].configure(text="FAIL")
                                                        self.output_file_pass[f"{key}"][f"{k}"][1] = check_version


                                                elif v[1] != "NA" and k == "NA":
                                                    # print("333")
                                                    check_version = locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n")
                                                    if check_version != "NA" and check_version != "":
                                                        if locals()[f"self.theme{key}"].get().strip(" ").strip("\n") != "NA" and locals()[f"self.theme{key}"].get().strip(" ").strip("\n") != "":
                                                            stage_name = locals()[f"self.theme{key}"].get().strip(" ").strip("\n")
                                                            if stage_name != "":
                                                                check_driver_stype = inst_dict[f"{stage_name}"]["AsName"].split("\\")[0].strip(" ").strip("\n")
                                                                locals()[f"self.browse_btn{key}_stpy"].configure(text=check_driver_stype)
                                                                locals()[f"self.browse_ver{key}"].configure(text=check_version)
                                                                locals()[f"self.check_pass{key}"].configure(bootstyle="success", text="PASS")

                                                                self.output_file_pass[f"{key}"] = {f"{stage_name}": [f"{check_driver_stype}",f"{check_version}"]}
                                                            else:
                                                                locals()[f"self.browse_btn{key}_stpy"].configure(text=k)
                                                                locals()[f"self.check_pass{key}"].configure(bootstyle="danger", text="FAIL")
                                                        else:
                                                            locals()[f"self.browse_btn{key}_stpy"].configure(text=k)
                                                            locals()[f"self.check_pass{key}"].configure(bootstyle="danger", text="FAIL")

                                                    else:
                                                        if locals()[f"self.theme{key}"].get().strip(" ").strip("\n") != "NA" and locals()[f"self.theme{key}"].get().strip(" ").strip("\n") != "":
                                                            stage_name = locals()[f"self.theme{key}"].get().strip(" ").strip("\n")
                                                            if stage_name != "":
                                                                check_driver_stype = inst_dict[f"{stage_name}"]["AsName"].split("\\")[0].strip(" ").strip("\n")
                                                                locals()[f"self.browse_btn{key}_stpy"].configure(text=check_driver_stype)
                                                                locals()[f"self.check_pass{key}"].configure(bootstyle="success", text="PASS")
                                                                self.output_file_pass[f"{key}"] = {f"{stage_name}":[f"{check_driver_stype}",f"{v[1]}"]}

                                                elif v[1] != "NA" and k != "NA":
                                                    # print("444")
                                                    check_version = locals()[f"self.check_ver{key}"].get().strip(" ").strip("\n")
                                                    if check_version != "NA" and check_version != "":
                                                        # print("替换")
                                                        # print(check_version)
                                                        locals()[f"self.browse_ver{key}"].configure(text=check_version)
                                                        self.output_file_pass[f"{key}"][f"{k}"][1] = check_version
                                                    else:
                                                        # print("修正")
                                                        # print(check_version)
                                                        locals()[f"self.browse_ver{key}"].configure(text=v[1])
                                                        self.output_file_pass[f"{key}"][f"{k}"][1] = v[1]


                                else:
                                    self.output_file_pass = self.check_it_pass

                        else:
                            Messagebox.show_error("有部分驱动包没有识别", title="ERROR")
        self.t2 = Thread(target=start_chk)
        # self.t2.setDaemon(True)
        self.t2.start()


    def on_browse1(self):
        """Callback for directory browse"""
        # path = askdirectory(title="Browse directory")
        # path = askopenfinilename(title="选择inst.ini文件")
        path = askopenfilename(title="选择inst.ini文件")
        if not path:
            return

        if path:
            self.path_var_inst.set(path)

    def on_browse2(self):
        """Callback for directory browse"""
        path = askdirectory(title="Browse directory")
        # path = askopenfilename(title="选择inst.ini文件")
        if not path:
            return

        if path:
            self.path_var_driver.set(path)

    def on_browse3(self):
        """Callback for directory browse"""
        # path = askdirectory(title="Browse directory")
        path = askopenfilename(title="选择新增租组件信息文件")
        if not path:
            return

        if path:
            self.path_var_comment.set(path)

    def on_browse5(self):
        """Callback for directory browse"""
        # path = askdirectory(title="Browse directory")
        path = askopenfilename(title="选择进行编译的XML文件")
        if not path:
            return

        if path:
            self.path_var_XML.set(path)

    def on_browse6(self):
        """Callback for directory browse"""
        path = askdirectory(title="Browse directory")
        # path = askopenfilename(title="选择inst.ini文件")
        if not path:
            return

        if path:
            self.path_var_DCD.set(path)

    def on_browse8(self):

        def discard_dcd():
            self.progressbar_dcd.config(bootstyle="Success-striped")
            self.progressbar_dcd["value"] = 5
            # self.progressbar_dcd_text.configure(text="5%", bootstyle=(SUCCESS, INVERSE))
            self.progressbar_dcd_text_value.set(value="50%")

            Driver_path = self.path_ent_dcd.get().strip(" ").strip("\n")
            if Driver_path:
                if os.path.exists(Driver_path):
                    os.chdir(Driver_path)
                    mount_file_path = os.getcwd()
                    mount_file_name = mount_file_path + "\mount"
                    if os.path.exists(mount_file_name):
                        file_list = os.listdir(mount_file_name)
                        if len(file_list) != 0:
                            canshu = self.theme_cbo2.get()

                            self.unmount_file(mount_file_name, canshu)
                            self.textbox_dcd.insert(END,
                                                    f"[{self.get_time()}] {mount_file_name} unmount file 完成\n")
                            self.progressbar_dcd["value"] = 10
                            self.progressbar_dcd_text_value.set(value="100%")
                        else:
                            print("文件为空 程式退出")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] {mount_file_name}为空可能文件没有保存完整\n")
                            try:
                                canshu = self.theme_cbo2.get()
                                self.unmount_file(mount_file_name, canshu)
                            except:

                                self.textbox_dcd.insert(END,
                                                        f"[{self.get_time()}] {mount_file_name}  file FAIL 可能mount 文件已经保存完整\n")
                                # sys.exit(0)
                            # else:
                            #     self.textbox_dcd.insert(END,
                            #                             f"[{self.get_time()}] {mount_file_name}unmount file 完成\n")
                            finally:
                                self.textbox_dcd.insert(END,
                                                        f"[{self.get_time()}] {mount_file_name} unmount file 完成\n")
                                self.progressbar_dcd["value"] = 10
                                self.progressbar_dcd_text_value.set(value="100%")
                            # sys.exit(0)
                    else:
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有发现{mount_file_name}文件夹的存在\n")
                        self.textbox_dcd.see(END)
                        self.progressbar_dcd["value"] = 0
                        self.progressbar_dcd_text_value.set(value="0%")
                        # sys.exit(0)

                else:
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 选择的DCD 路径不正确{Driver_path}\n")
                    self.textbox_dcd.see(END)
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")

                    # Messagebox.show_error(f"选择的DCD 路径不正确{Driver_path}", title="ERROR")

            else:
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有选择需要不保存的Driver CD\n")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 请选择DCD 路径后再重新的按discard 功能\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                # Messagebox.show_error("没有选择需要不保存的Driver CD", title="ERROR")

        self.t3 = Thread(target=discard_dcd)
        self.t3.setDaemon(True)
        self.t3.start()

    def on_browse9(self):

        def mount_dcd():
            self.progressbar_dcd.config(bootstyle="Success-striped")
            self.progressbar_dcd["value"] = 5
            self.progressbar_dcd_text_value.set(value="50%")
            Driver_path = self.path_ent_dcd.get().strip(" ").strip("\n")
            if Driver_path:
                mount_file_name = self.mount_file(Driver_path)
                if mount_file_name:
                    self.textbox_dcd.insert(END,f"[{self.get_time()}] {Driver_path} mount file 完成\n")
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.progressbar_dcd_text.config(text="10%", bootstyle=(SUCCESS, INVERSE))
                else:
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] {Driver_path} 文件不为空 \n")
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")

            else:
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有选择需要mount的Driver CD\n")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 请选择DCD 路径后再重新的按mount_ 功能\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")

        #     if os.path.exists(Driver_path):
            #         os.chdir(Driver_path)
            #         mount_file_path = os.getcwd()
            #         mount_file_name = mount_file_path + "\mount"
            #         if os.path.exists(mount_file_name):
            #             file_list = os.listdir(mount_file_name)
            #             if len(file_list) != 0:
            #                 canshu = "discard"
            #                 self.unmount_file(mount_file_name, canshu)
            #                 self.textbox_dcd.insert(END,
            #                                         f"[{self.get_time()}] {mount_file_name} unmount file 完成\n")
            #                 self.progressbar_dcd["value"] = 10
            #             else:
            #                 print("文件为空 程式退出")
            #                 self.textbox_dcd.insert(END,
            #                                         f"[{self.get_time()}] {mount_file_name}为空可能文件没有保存完整\n")
            #                 try:
            #                     canshu = "discard"
            #                     self.unmount_file(mount_file_name, canshu)
            #                 except:
            #
            #                     self.textbox_dcd.insert(END,
            #                                             f"[{self.get_time()}] {mount_file_name}  file FAIL 可能mount 文件已经保存完整\n")
            #                     sys.exit(0)
            #                 # else:
            #                 #     self.textbox_dcd.insert(END,
            #                 #                             f"[{self.get_time()}] {mount_file_name}unmount file 完成\n")
            #                 finally:
            #                     self.textbox_dcd.insert(END,
            #                                             f"[{self.get_time()}] {mount_file_name} unmount file 完成\n")
            #                     self.progressbar_dcd["value"] = 10
            #                 # sys.exit(0)
            #         else:
            #             self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有发现{mount_file_name}文件夹的存在\n")
            #             self.textbox_dcd.see(END)
            #             self.progressbar_dcd["value"] = 0
            #             sys.exit(0)
            #
            #     else:
            #         self.textbox_dcd.insert(END, f"[{self.get_time()}] 选择的DCD 路径不正确{Driver_path}\n")
            #         self.textbox_dcd.see(END)
            #         self.progressbar_dcd["value"] = 10
            #         self.progressbar_dcd.config(bootstyle="danger-striped")
            #         # Messagebox.show_error(f"选择的DCD 路径不正确{Driver_path}", title="ERROR")
            #
            # else:
            #     self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有选择需要不保存的Driver CD\n")
            #     self.textbox_dcd.insert(END, f"[{self.get_time()}] 请选择DCD 路径后再重新的按discard 功能\n")
            #     self.textbox_dcd.see(END)
            #     self.progressbar_dcd["value"] = 10
            #     self.progressbar_dcd.config(bootstyle="danger-striped")
            #     # Messagebox.show_error("没有选择需要不保存的Driver CD", title="ERROR")

        self.t4 = Thread(target=mount_dcd)
        self.t4.setDaemon(True)
        self.t4.start()


    def get_time(self):
        now_time = datetime.datetime.now().strftime('%H:%M:%S')
        if now_time:
            return now_time

    # 获取文件的类型
    def check_file_type(self, file):

        if os.path.exists(file):
            with open(f"{file}", "rb") as f:
                date = f.read()
            result = chardet.detect(date)
            read_type = result["encoding"]
            if read_type:
                return read_type
            else:
                return False
        else:
            print("文件不存在")
            return False

    # 获取inst.ini文件的信息
    def getinstinfo(self, file):

        file_path = file  # 调用全局变量
        items = {}
        items_list = {}  # 创建一个列表准备接受 [Stage 60] 到下一个[Stage 60]之间的所有数据
        tiger = "NA"  # 准备做一个标志位置
        read_type = self.check_file_type(file_path)
        if read_type:
            with open(file_path, "r", encoding=f'{read_type}') as file:
                ck = "(^\[.*\]$)"
                while True:
                    line = file.readline()
                    if re.search(ck, line):
                        tiger = "YES"  # 改变标志位的内容
                        items_list = {}  # 重新置空列表
                        r = re.search(ck, line)
                        disk_key = r.group(0)
                        items[disk_key] = items_list  # 将以标志位来接受他的所有数据,这里已经定义了一个值来拿p
                        continue
                    if tiger != "NA":
                        # 这步的意思就是将后面的单个选项做成一个字典的形式 然否将字典的形式 储蓄在列表中去
                        # keys_items = {}
                        if len(line.split("=")) >= 2:
                            keys = line.split("=")[0]
                            # keys_items[f"{keys}"] = line.split("=")[1]
                            items[disk_key][f"{keys}"] = line.split("=")[1]
                            continue
                        else:
                            items[disk_key][line] = line
                            # time.sleep(2)
                    if not line:
                        break
        else:
            print("error")
            print("文件读取FAIL 格式错误或者文件不存在")
        if items:
            return items
        else:
            return False

    # 获取驱动文件的inf 文件信息
    def change_version(self,file_ver):
        if file_ver:
            inf_ver_list = file_ver.split(".")
            inf_ver_list_shouji = []
            driver_ver = ""
            for i in inf_ver_list:
                if len(i) > 1 and i[0] == '0':
                    inf_ver_list_shouji.append(i[1:])
                else:
                    inf_ver_list_shouji.append(i)
            else:
                driver_ver = ".".join(inf_ver_list_shouji)
            if driver_ver:
                return driver_ver
            else:
                return False


    def get_inf(self, file_path, inst_file):
        # get_inf 这里需要再改一下这里在确定有file.json的情况 不需要inst.ini的介入
        if os.path.exists(f"{file_path}\\file.json"):
            # print("funckkkkkk")
            json_file = f"{file_path}\\file.json"
            #需要将json 文档转换为py的数据类型 的到一个字典信息
            diver_file_info = self.switchtoPy(json_file)
            #获取组件包里面的全部信息
            file_path_list = os.listdir(file_path)
            #收集驱动组件的信息
            inf_disk = {}

            # 标志位 判断是否存在inf文档和是否检测到version 如果没有检测到 统统报错


            for key, value in diver_file_info.items():
                # print(key,value)
                for k, v in value.items():
                    # 这里就要开始区分区间包的类型了{"05.Intel_Graphics_31.0.101.3887": {"[Stage 74]": ["Driver", "31.0.101.3887"]}
                    #  "11_1.Rtk_Audio_UWP_1.40.286.0": {"[Stage 158]": ["StoreAPP", "1.40.286.0"]}
                    # 是否压迫确定inst.ini已经被拿掉呢 这样去比较是不是有问题
                    driver_ver = v[1].strip("\n").strip(" ").strip("\t")
                    key = key.strip("\n").strip(" ").strip("\t")
                    if v[0].upper() == "DRIVER":
                        self.is_exist_inf = False
                        self.is_find_verison = False
                        date_time = {}
                        for file_name in file_path_list:
                            # 将数据path 进行处理
                            file_name = file_name.strip("\n").strip(" ").strip("\t")
                            if file_name == key:
                                abs_path = os.path.join(file_path, file_name)
                                if os.path.isdir(abs_path):
                                    for root, dirs, files in os.walk(abs_path):
                                        for file in files:
                                            file = file.lower()
                                            targers = r".inf"
                                            if file.find(f"{targers}") != -1:
                                                # 设置一个标志的位置判断是否有inf文档
                                                # print("==============")
                                                # print(file)
                                                # print(key)
                                                # print("==============")
                                                self.is_exist_inf = True
                                                inf_path = os.path.join(root, file)
                                                read_type = self.check_file_type(inf_path)

                                                with open(f"{inf_path}", "r", encoding=read_type) as fd:
                                                    while True:
                                                        line = fd.readline()
                                                        # 03.00.00.1457
                                                        if line.find("DriverVer") != -1:
                                                            if line.find(f"{driver_ver}") != -1:
                                                                self.is_find_verison = True
                                                                # print(key)
                                                                date_time[f'{driver_ver}'] = ("-").join(line.split("=")[1].split(",")[0].split("/"))
                                                                inf_disk[f"{key}"] = date_time
                                                                break
                                                            else:
                                                                # inf_ver_list = ""
                                                                # 这里可以做个判断是否是那种坑壁的version版本格式10.29.00.8365
                                                                # 这里要做一个数据的处理
                                                                # 遇到这种坑比的数据也是醉了DriverVer = 10/18/2022,22.180.0.4 ;DATE HAS TO BE IN FOLLOWING FORMAT MM/DD/YYYY

                                                                # ck1 = r"[,;]"
                                                                if line.find(";") != -1:
                                                                    inf_ver_list = line.split("=")[1].split(",")[1].strip(" ").strip("\n").strip("\t")
                                                                else:
                                                                    ck1 = r"[,;]"
                                                                    inf_ver_list = re.split(ck1,line)[1]
                                                                if inf_ver_list:
                                                                    inf_ver = self.change_version(inf_ver_list).strip(" ").strip("\n").strip("\t")
                                                                    driver_ver_check = self.change_version(driver_ver).strip(" ").strip("\n").strip("\t")
                                                                    print(driver_ver_check, inf_ver)
                                                                    if inf_ver and driver_ver_check:
                                                                        if inf_ver == driver_ver_check:
                                                                            self.is_find_verison = True
                                                                            date_time[f'{driver_ver}'] = ("-").join(line.split("=")[1].split(",")[0].split("/"))
                                                                            inf_disk[f"{key}"] = date_time
                                                                            break
                                                                else:
                                                                    self.textbox.insert(END,f"[{self.get_time()}][ERROR] {key} 标记的version{driver_ver},inf_ver 版本获取fail\n")
                                                                    Messagebox.show_error(f"{key} 标记的version{driver_ver},inf_ver 版本获取fail",title="ERROR")
                                                                    break

                                                        if not line:
                                                            break
                                            else:
                                                continue
                                    else:
                                        if not self.is_exist_inf:
                                            self.textbox.insert(END,f"[{self.get_time()}] [ERROR] {key}没有发现该驱动组件的inf文档\n")
                                            Messagebox.show_error(f"{key}没有发现该驱动组件的inf文档",title="ERROR")
                                            break
                                        elif not self.is_find_verison:
                                            self.textbox.insert(END, f"[{self.get_time()}] [ERROR] {key} 标记的version{driver_ver},在驱动组件包里面的inf档中没有被发现\n")
                                            Messagebox.show_error(f"{key} 标记的{driver_ver}版本,在驱动组件包里面的inf档中没有被发现",title="ERROR")
                                            break

                    elif  v[0].upper() == "STOREAPP":
                        inf_disk[f"{key}"] = driver_ver
                        continue
                    elif v[0].upper() == "WIN32APP":
                        inf_disk[f"{key}"] = driver_ver
                        continue
                    elif v[0].upper() == "COMPONENT":
                        inf_disk[f"{key}"] = driver_ver
                        continue
                    else:
                        # print(f"文件包有异常{driver_name}，该文件包尚未在inst.ini文件中找到")
                        self.textbox.insert(END,f"[{self.get_time()}][ERROR] 文件包有异常{key}，该文件包尚未在inst.ini文件中找到\n")

        else:
            # file_path = r"C:\Users\易守林\Desktop\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR"
            inst_list = self.getinstinfo(inst_file)
            file_path_list = os.listdir(file_path)
            inf_disk = {}

            # 标志位 判断是否存在inf文档和是否检测到version 如果没有检测到 统统报错
            self.is_exist_inf = False
            self.is_find_verison = False

            for path in file_path_list:
                path = os.path.join(file_path, path)
                if os.path.isdir(path):
                    driver_name = path.split("\\")[-1]
                    ck = "(^\d.*\d*$)"
                    if re.findall(ck, driver_name):
                        ck1 = r"[-_]"
                        date_time = {}
                        # driver_ver = driver_name.split("_")[-1]
                        if re.findall("(^\d?\d$)", re.split(ck1, driver_name)[0]):
                            inst_driver_name = "_".join(re.split(ck1, driver_name)[0:2])
                        else:
                            inst_driver_name = re.split(ck1, driver_name)[0]

                        driver_ver = re.split(ck1,driver_name)[-1]

                        for k, v in inst_list.items():
                            for kk, vv in v.items():
                                if vv.find(inst_driver_name) != -1:
                                    if v["AsName"].split("\\")[0].upper() == "DRIVER":
                                        for root, dirs, files in os.walk(path):
                                            for file in files:
                                                file = file.lower()
                                                targers = r".inf"
                                                if file.find(f"{targers}") != -1:
                                                    self.is_exist_inf = True
                                                    path = os.path.join(root, file)
                                                    read_type = self.check_file_type(path)
                                                    with open(f"{path}", "r", encoding=read_type) as fd:
                                                        # print(file)
                                                        while True:
                                                            line = fd.readline()
                                                            if line.find("DriverVer") != -1 and line.find(
                                                                    f"{driver_ver}") != -1:
                                                                self.is_find_verison = True
                                                                date_time[f'{driver_ver}'] = ("-").join(line.split("=")[1].split(",")[0].split("/"))
                                                                # date_time[f'{("-").join(line.split("=")[1].split(",")[0].split("/"))}'] = driver_ver
                                                                inf_disk[f"{driver_name}"] = date_time
                                                                continue
                                                            if not line:
                                                                break
                                                else:
                                                    continue
                                        else:
                                            if not self.is_exist_inf:
                                                self.textbox.insert(END,f"[{self.get_time()}][ERROR] {driver_name}没有发现该驱动组件的inf文档\n")
                                                Messagebox.show_error(f"{driver_name}没有发现该驱动组件的inf文档")

                                                sys.exit(0)
                                            elif not self.is_find_verison:
                                                self.textbox.insert(END,f"[{self.get_time()}] [ERROR] 标记的version{driver_ver},在驱动组件包里面的inf档中没有被发现\n")
                                                Messagebox.show_error(f"{driver_name} 标记的version{driver_ver},在驱动组件包里面的inf档中没有被发现")
                                                sys.exit(0)

                                    elif v["AsName"].split("\\")[0].upper() == "STOREAPP":
                                        inf_disk[f"{driver_name}"] = driver_ver
                                        continue
                                    elif v["AsName"].split("\\")[0].upper() == "WIN32APP":
                                        inf_disk[f"{driver_name}"] = driver_ver
                                        continue
                                    elif v["AsName"].split("\\")[0].upper() == "COMPONENT":
                                        inf_disk[f"{driver_name}"] = driver_ver
                                        continue
                                    else:
                                        # print(f"文件包有异常{driver_name}，该文件包尚未在inst.ini文件中找到")
                                        self.textbox.insert(END, f"[{self.get_time()}] [ERROR] 文件包有异常{driver_name}，该文件包尚未在inst.ini文件中找到\n")

                    else:
                        print(f"文件名字不对{driver_name}")

                        continue
                else:
                    continue
        # print(inf_disk)
        if len(inf_disk.keys()) == len(file_path_list):
            not_in = []
            for i in file_path_list:
                if i not in inf_disk.keys():
                    # print(f"组件包{i},没有被inst.ini里面识别到")
                    not_in.append(i)
                else:
                    continue
            if len(not_in) == 0:
                return inf_disk
            else:
                print(not_in)
                return False
        else:
            not_in = []
            for i in file_path_list:
                path = os.path.join(file_path, i)
                if os.path.isdir(path):
                    if i not in inf_disk.keys():
                        # print(f"组件包{i},没有被inst.ini里面识别到")
                        not_in.append(i)
                    else:
                        continue
                else:
                    self.textbox.insert(END, f"[{self.get_time()}] [警告]在驱动包里面以下{path}不是文件包\n")
            if len(not_in) == 0:
                # print(inf_disk)
                return inf_disk

            else:
                resuit = tkinter.messagebox.askquestion( title=f"确认是否忽略该组件",message=f"有{not_in}部分未在inst.ini")
                print(resuit)
                if resuit == "yes":
                    return inf_disk
                else:
                    self.textbox.insert(END, f"[{self.get_time()}] [ERROR] 有{not_in}部分组件没有被inst xml buils fail\n")
                    return False


    # build XML的主要函数就是这个
    def build_and_check_xml(self, inst_file, file_path, Dcd_Name, xml_name, Stage_bao):

        if os.path.exists(f"{file_path}\\file.json"):
            self.textbox.insert(END, f"[{self.get_time()}] 确定组件文件里面有file.json文件\n")
            json_file = f"{file_path}\\file.json"
            # 需要将json 文档转换为py的数据类型 的到一个字典信息
            """
                {
                '05.Intel_Graphics_31.0.101.3887': {'[Stage 74]': ['Driver', '31.0.101.3887']}, 
                '1.ddddddd': {'[Stage 88]': ['Driver', '2.3.4.5']}, 
                '11.RTK_Codec_6.0.9445.1': {'[Stage 82]': ['Driver', '6.0.9445.1']}, 
                '11_1.Rtk_Audio_UWP_1.40.286.0': {'[Stage 158]': ['StoreAPP', '1.40.286.0']}, 
                '12.Dolby_APO_7.1128.706.52': {'[Stage 102]': ['Driver', '7.1128.706.52']}, 
                '12_1.Dolby_UWP_3.15.694.0': {'[Stage 106]': ['StoreAPP', '3.15.694.0']}, 
                '16.NVIDIA_GFX_31.0.15.2717': {'[Stage 76]': ['Driver', '31.0.15.2717']}, 
                '18.Numberpad_17.0.0.13': {'[Stage 98]': ['Driver', '17.0.0.13']}, 
                '19.Morpho_AI_Camera_1.0.4.5': {'[Stage 148]': ['Driver', '1.0.4.5']}
                }
            """
            diver_file_info = self.switchtoPy(json_file)
            # if Stage_bao == "NA":
            #确定Driver CD 的版本信息
            Driver_CD_ver = Dcd_Name.split("_")[-1]
            #得到inst.ini的信息
            inst_list = self.getinstinfo(inst_file)
            #得到驱动包的全部组件信息
            driver_file_bao = os.listdir(file_path)
            # 如果去是驱动的话需要提前获取到驱动包里面的版本信息和日期
            """
                
                {
                    '05.Intel_Graphics_31.0.101.3887': {'31.0.101.3887': '10-26-2022'}, 
                    '11.RTK_Codec_6.0.9445.1': {'6.0.9445.1': ' 11-22-2022'}, 
                    '11_1.Rtk_Audio_UWP_1.40.286.0': '1.40.286.0', 
                    '12.Dolby_APO_7.1128.706.52': {'7.1128.706.52': ' 11-27-2022'}, 
                    '16.NVIDIA_GFX_31.0.15.2717': {'31.0.15.2717': ' 11-21-2022'}, 
                    '18.Numberpad_17.0.0.13': {'17.0.0.13': ' 11-21-2022'}, 
                    '19.Morpho_AI_Camera_1.0.4.5': {'1.0.4.5': ' 11-19-2022'}
                }
            """
            inf_disk = self.get_inf(file_path, inst_file)
            if inf_disk:
                doc = xml.dom.minidom.Document()
                root = doc.createElement('root')
                Part = doc.createElement('Part')
                Part.setAttribute("Describ", "Driver_CD")
                Part.setAttribute("version", f"{Driver_CD_ver}")
                Part.setAttribute("modid", f"{Dcd_Name}")
                doc.appendChild(root)
                root.appendChild(Part)
                for driver_file_bao_path in driver_file_bao:
                    #这里还是相对路径 所以要增加一个绝对路径
                    driver_file_bao_path = driver_file_bao_path.strip("\n").strip(" ").strip("\t")
                    abs_path = os.path.join(file_path, driver_file_bao_path)
                    if os.path.isdir(abs_path):
                        for key, value in diver_file_info.items():
                            if driver_file_bao_path == key:
                                for k, v in value.items():
                                    if v[0].upper() == "DRIVER":
                                        file_date = inf_disk[f'{key}'][v[1]].strip(" ")
                                        file_ver = v[1].strip("\n").strip(" ").strip("\t")
                                        Part = doc.createElement('Part')
                                        Part.setAttribute("Describ", "DRIVER")
                                        Driver_name = inst_list[k]['APP_Name'].strip('\n')
                                        Part.setAttribute("Name", f"{Driver_name}")
                                        Part.setAttribute("Stage", f"{k}")
                                        Part.setAttribute("Date", f"{file_date}")
                                        Part.setAttribute("version", f"{file_ver}")
                                        Part.setAttribute("FilePath", f"{abs_path}")
                                        Part.setAttribute("HWID", "")
                                        Part.setAttribute("Type", "")
                                        root.appendChild(Part)
                                    elif v[0].upper() == "STOREAPP":
                                        Part = doc.createElement('Part')
                                        Part.setAttribute("Describ", "STOREAPP")
                                        Driver_name = inst_list[k]['APP_Name'].strip('\n')
                                        file_ver = v[1].strip("\n").strip(" ").strip("\t")
                                        Part.setAttribute("Name", f"{Driver_name}")
                                        Part.setAttribute("Stage", f"{k}")
                                        Part.setAttribute("version", f"{file_ver}")
                                        Part.setAttribute("FilePath", f"{abs_path}")
                                        root.appendChild(Part)
                                    elif v[0].upper() == "WIN32APP":
                                        Part = doc.createElement('Part')
                                        Part.setAttribute("Describ", "WIN32APP")
                                        Driver_name = inst_list[k]['APP_Name'].strip('\n')
                                        file_ver = v[1].strip("\n").strip(" ").strip("\t")
                                        Part.setAttribute("Name", f"{Driver_name}")
                                        Part.setAttribute("Stage", f"{k}")
                                        Part.setAttribute("version", f"{file_ver}")
                                        Part.setAttribute("FilePath", f"{abs_path}")
                                        root.appendChild(Part)
                                    elif v[0].upper() == "COMPONENT":
                                        Part = doc.createElement('Part')
                                        Part.setAttribute("Describ", "COMPONENT")
                                        Driver_name = inst_list[k]['APP_Name'].strip('\n')
                                        file_ver = v[1].strip("\n").strip(" ").strip("\t")
                                        Part.setAttribute("Name", f"{Driver_name}")
                                        Part.setAttribute("Stage", f"{k}")
                                        Part.setAttribute("version", f"{file_ver}")
                                        Part.setAttribute("FilePath", f"{abs_path}")
                                        root.appendChild(Part)
                if Stage_bao != "NA":
                    # 将new的组件信息复制到XML文件中去
                    # new_comment_list = self.getinstinfo(Stage_bao)
                    targer = os.path.splitext(os.path.basename(f"{Stage_bao}"))[0]
                    Part = doc.createElement('Part')
                    Part.setAttribute("Describ", "ADDCOMMENT")
                    Part.setAttribute("targer", f"{targer}")
                    Part.setAttribute("commentinfo", f"{Stage_bao}")
                    root.appendChild(Part)

                os.getcwd()
                # print(os.getcwd())
                fp = open(f'{xml_name}.xml', 'w', encoding='utf-8')  # 需要指定utf-8的文件编码格式，不然notepad中显示十六进制
                doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')
                fp.close()
                # print("XML 已经BUILD PASS")
                self.textbox.insert(END, f"[{self.get_time()}] {self.xml_name}.xml已经build PASS\n")
                Messagebox.show_info(f"{self.xml_name}.xml已经build PASS", title="XML Build PASS")
            else:
                self.textbox.insert(END, f"[{self.get_time()}] 获取到inf_disk：{inf_disk}的值\n")
                print(f"获取到inf_disk：{inf_disk}的值")
                Messagebox.show_error(f"获取到inf_disk：{inf_disk}的值", title="get_inf info fail")
        else:

            if Stage_bao == "NA":
                # 这里需要进行文件的分流 json 上场
                # if os.path.exists(f"{file_path}\\file.json"):
                Dcd_Ver = Dcd_Name.split("_")[-1]
                inst_list = self.getinstinfo(inst_file)
                # print(inst_list)
                # file_path 是驱动包
                file_list = os.listdir(file_path)
                #============================================
                inf_disk = self.get_inf(file_path, inst_file)
                # ============================================
                # 说明是获取到了 inf的
                if inf_disk:
                    # print(inf_disk)
                    # <Part Describ="Driver_CD" version="1.00" modid="X64W11_22H2_SWP_UX3404VA_01.00"/>
                    doc = xml.dom.minidom.Document()
                    root = doc.createElement('root')
                    Part = doc.createElement('Part')
                    Part.setAttribute("Describ", "Driver_CD")
                    Part.setAttribute("version", f"{Dcd_Ver}")
                    Part.setAttribute("modid", f"{Dcd_Name}")
                    doc.appendChild(root)
                    root.appendChild(Part)
                    for i in file_list:
                        # 判断是否为文件
                        if os.path.isdir(f"{file_path}\\{i}"):
                            file_asdpath = os.path.join(file_path, i)
                            # 我需要获取的几个信息是 driver、stage，APP_Name ，AsName=
                            # 01.Intel_Chipset_10.1.36.7
                            # file_ver = i.split("_")[-1]
                            # print(f"{i}")

                            if i in inf_disk.keys():
                                ck = "(^\d.*\d$)"
                                if re.findall(ck, i):
                                    # print(driver_name)
                                    # 确定的名字的规范后 看是否在inst.ini
                                    ck1 = r"[-_]"
                                    if re.findall("(^\d?\d$)", re.split(ck1, i)[0]):
                                        file_name = "_".join(re.split(ck1, i)[0:2])
                                    else:
                                        file_name = re.split(ck1, i)[0]
                                file_ver = re.split(ck1, i)[-1]

                                for k, v in inst_list.items():
                                    for kk, vv in v.items():
                                        if vv.find(file_name) != -1:
                                            if v["AsName"].split("\\")[0].upper() == "DRIVER":
                                                file_date = inf_disk[f'{i}'][f'{file_ver}'].strip(" ")
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "DRIVER")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("Date", f"{file_date}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                Part.setAttribute("HWID", "")
                                                Part.setAttribute("Type", "")
                                                root.appendChild(Part)
                                            elif v["AsName"].split("\\")[0].upper() == "STOREAPP":
                                                # file_date = inf_disk[f'{i}']
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "STOREAPP")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                root.appendChild(Part)
                                            elif v["AsName"].split("\\")[0].upper() == "WIN32APP":
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "WIN32APP")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                root.appendChild(Part)
                                            elif v["AsName"].split("\\")[0].upper() == "COMPONENT":
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "COMPONENT")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                root.appendChild(Part)

                        else:
                            Messagebox.show_error(F"非文件包：{i}，不会被BUILD", title=f"非文件包：{i}，不会被BUILD")
                            continue

                    # os.getcwd()
                    # 将生成的XML文档生成在EXE的那个文档下面去
                    os.chdir(self.py_path)
                    # print(os.getcwd())
                    fp = open(f'{xml_name}.xml', 'w', encoding='utf-8')  # 需要指定utf-8的文件编码格式，不然notepad中显示十六进制
                    doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')
                    fp.close()
                    self.textbox.insert(END, f"[{self.get_time()}] {self.xml_name}.xml已经build PASS\n")
                    Messagebox.show_info(f"{self.xml_name}.xml已经build PASS", title="XML Build PASS")

                else:
                    self.textbox.insert(END, f"[{self.get_time()}] 获取到inf_disk：{inf_disk}的值\n")
                    print(f"获取到inf_disk：{inf_disk}的值")
                    Messagebox.show_error(f"获取到inf_disk：{inf_disk}的值", title="get_inf info fail")
                    # sys.exit(0)
            else:
                Dcd_Ver = Dcd_Name.split("_")[-1]
                inst_list = self.getinstinfo(inst_file)
                # print(inst_list)
                file_list = os.listdir(file_path)
                inf_disk = self.get_inf(file_path, inst_file)
                if inf_disk:
                    # print(inf_disk)
                    # <Part Describ="Driver_CD" version="1.00" modid="X64W11_22H2_SWP_UX3404VA_01.00"/>
                    doc = xml.dom.minidom.Document()
                    root = doc.createElement('root')
                    Part = doc.createElement('Part')
                    Part.setAttribute("Describ", "Driver_CD")
                    Part.setAttribute("version", f"{Dcd_Ver}")
                    Part.setAttribute("modid", f"{Dcd_Name}")
                    doc.appendChild(root)
                    root.appendChild(Part)
                    for i in file_list:
                        # 判断是否为文件
                        if os.path.isdir(f"{file_path}\\{i}"):
                            file_asdpath = os.path.join(file_path, i)
                            # 我需要获取的几个信息是 driver、stage，APP_Name ，AsName=
                            # 01.Intel_Chipset_10.1.36.7
                            file_ver = i.split("_")[-1]
                            # print(f"{i}")

                            if i in inf_disk.keys():
                                #
                                file_name = "_".join(i.split("_")[:-1])
                                for k, v in inst_list.items():
                                    for kk, vv in v.items():
                                        if vv.find(file_name) != -1:
                                            if v["AsName"].split("\\")[0].upper() == "DRIVER":
                                                file_date = inf_disk[f'{i}'][f'{file_ver}'].strip(" ")
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "DRIVER")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("Date", f"{file_date}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                Part.setAttribute("HWID", "")
                                                Part.setAttribute("Type", "")
                                                root.appendChild(Part)
                                            elif v["AsName"].split("\\")[0].upper() == "STOREAPP":
                                                # file_date = inf_disk[f'{i}']
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "STOREAPP")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                root.appendChild(Part)
                                            elif v["AsName"].split("\\")[0].upper() == "WIN32APP":
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "WIN32APP")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                root.appendChild(Part)
                                            elif v["AsName"].split("\\")[0].upper() == "COMPONENT":
                                                Part = doc.createElement('Part')
                                                Part.setAttribute("Describ", "COMPONENT")
                                                Driver_name = v['APP_Name'].strip('\n')
                                                Part.setAttribute("Name", f"{Driver_name}")
                                                Part.setAttribute("Stage", f"{k}")
                                                Part.setAttribute("version", f"{file_ver}")
                                                Part.setAttribute("FilePath", f"{file_asdpath}")
                                                root.appendChild(Part)


                        else:
                            print(f'非文件包：{i}，不会被BUILD')
                            Messagebox.show_error(F"非文件包：{i}，不会被BUILD", title=f"非文件包：{i}，不会被BUILD")
                            continue

                    # 将new的组件信息复制到XML文件中去
                    # new_comment_list = self.getinstinfo(Stage_bao)
                    targer = os.path.splitext(os.path.basename(f"{Stage_bao}"))[0]
                    Part = doc.createElement('Part')
                    Part.setAttribute("Describ", "ADDCOMMENT")
                    Part.setAttribute("targer", f"{targer}")
                    Part.setAttribute("commentinfo", f"{Stage_bao}")
                    root.appendChild(Part)
                    # print("qqqqqq")

                    os.getcwd()
                    # print(os.getcwd())
                    fp = open(f'{xml_name}.xml', 'w', encoding='utf-8')  # 需要指定utf-8的文件编码格式，不然notepad中显示十六进制
                    doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')
                    fp.close()
                    # print("XML 已经BUILD PASS")
                    self.textbox.insert(END, f"[{self.get_time()}] {self.xml_name}.xml已经build PASS\n")
                    Messagebox.show_info(f"{self.xml_name}.xml已经build PASS", title="XML Build PASS")
                else:
                    # print(f"获取到inf_disk：{inf_disk}的值")
                    self.textbox.insert(END, f"[{self.get_time()}] 获取到inf_disk：{inf_disk}的值\n")
                    # sys.exit(0)


    def on_browse4(self):

        os.chdir(self.py_path)
        # self.progressbar["value"] = 1
        self.textbox.insert(END, f"[{self.get_time()}] Start Build XML\n")
        # self.progressbar["value"] = 2
        # 开始获取各个的参数
        # inst_file = r"C:\Users\Ben\Desktop\X64W11_22H2_SWP_UX3404VA_01.00\inst.ini"
        # file_path = r"C:\Users\Ben\Desktop\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V101_for_PR"
        # Dcd_Name = r"X64W11_22H2_SWP_UX3404VA_01.00_Test_1"
        # build_and_check_xml(inst_file, file_path, Dcd_Name)
        # search_term = self.term_var.get()
        # search_path = self.path_var.get()
        # search_type = self.type_var.get()
        # Driver Name
        self.driver_name = self.path_ent.get().strip(" ").strip("\n")
        # XML Name
        self.xml_name = self.path_ent1.get().strip(" ").strip("\n")
        # Inst.ini File
        self.inst_file = self.path_ent_inst.get().strip(" ").strip("\n")
        # 驱动安装包
        self.driver_bao = self.path_ent_driver.get().strip(" ").strip("\n")
        # Stage组件
        self.Stage_bao = self.path_ent_Stage.get().strip(" ").strip("\n")
        if self.driver_name:
            self.textbox.insert(END, f"[{self.get_time()}] 输入的Driver CD 名字：{self.driver_name}\n")
        # self.textbox.insert(END, "\n")
        if self.xml_name:
            self.textbox.insert(END, f"[{self.get_time()}] 输入的XML名字：{self.xml_name}\n")
        # self.textbox.insert(END, "\n")
        if self.inst_file:
            self.textbox.insert(END, f"[{self.get_time()}] 选择的inst.ini文件：{self.inst_file}\n")
        # self.textbox.insert(END, "\n")
        if self.driver_bao:
            self.textbox.insert(END, f"[{self.get_time()}] 选择的驱动安装文件包：{self.driver_bao}\n")
        # self.textbox.insert(END, "\n")
        if self.Stage_bao:
            self.textbox.insert(END, f"[{self.get_time()}] 选择增加的组件ini文件：{self.Stage_bao}\n")
        # self.textbox.insert(END, "\n")
        # self.progressbar["value"] = 3
        if self.driver_name and self.xml_name:
            # self.progressbar["value"] = 4
            # 这两个是必要选项
            # 这三者全部为空的时候，只更新
            # 但是也必须将Driver CD 的名字也需要更新进入
            if not self.inst_file and not self.driver_bao and not self.Stage_bao:
                Dcd_Ver = self.driver_name.split("_")[-1]
                Messagebox.ok(message='将只会更新inst.ini等文件 To DCD 文件包中 并重新封包Driver')
                doc = xml.dom.minidom.Document()
                root = doc.createElement('root')
                Part = doc.createElement('Part')
                Part.setAttribute("Describ", "Driver_CD")
                Part.setAttribute("version", f"{Dcd_Ver}")
                Part.setAttribute("modid", f"{self.driver_name}")
                doc.appendChild(root)
                root.appendChild(Part)
                Part = doc.createElement('Part')
                Part.setAttribute("Describ", "Update")
                root.appendChild(Part)

                os.getcwd()
                # print(os.getcwd())
                fp = open(f'{self.xml_name}.xml', 'w', encoding='utf-8')  # 需要指定utf-8的文件编码格式，不然notepad中显示十六进制
                doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')
                fp.close()
                self.textbox.insert(END, f"[{self.get_time()}] {self.xml_name}.xml已经build PASS\n")
                Messagebox.show_info(f"{self.xml_name}.xml已经build PASS", title="XML Build PASS")

            elif self.inst_file and self.driver_bao:
                if self.Stage_bao:
                    self.build_and_check_xml(self.inst_file, self.driver_bao, self.driver_name, self.xml_name,
                                             self.Stage_bao)
                else:
                    self.Stage_bao = "NA"
                    self.build_and_check_xml(self.inst_file, self.driver_bao, self.driver_name, self.xml_name, self.Stage_bao)
                    # print("ssss")

            elif not self.inst_file and not self.driver_bao and self.Stage_bao:
                Dcd_Ver = self.driver_name.split("_")[-1]

                doc = xml.dom.minidom.Document()
                root = doc.createElement('root')
                Part = doc.createElement('Part')
                Part.setAttribute("Describ", "Driver_CD")
                Part.setAttribute("version", f"{Dcd_Ver}")
                Part.setAttribute("modid", f"{self.driver_name}")
                doc.appendChild(root)
                root.appendChild(Part)
                # new_comment_list = self.getinstinfo(self.Stage_bao)
                targer = os.path.splitext(os.path.basename(f"{self.Stage_bao}"))[0]
                Part = doc.createElement('Part')
                Part.setAttribute("Describ", "ADDCOMMENT")
                Part.setAttribute("targer", f"{targer}")
                Part.setAttribute("commentinfo", f"{self.Stage_bao}")
                root.appendChild(Part)
                os.getcwd()
                # print(os.getcwd())
                fp = open(f'{self.xml_name}.xml', 'w', encoding='utf-8')  # 需要指定utf-8的文件编码格式，不然notepad中显示十六进制
                doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')
                fp.close()
                self.textbox.insert(END, f"[{self.get_time()}] {self.xml_name}.xml已经build PASS\n")
                # Messagebox.ok(message='将只会更新inst.ini等文件 To DCD 文件包中 并重新封包Driver')
                Messagebox.show_info("f{self.xml_name}.xml已经build PASS",title="XML Build PASS")
            elif self.inst_file and not self.driver_bao:
                self.textbox.insert(END, f"[{self.get_time()}] {self.xml_name}.如果选择了inst.ini 文件 但是却没有选择driver 包的话 这样是不是build XML文件的\n")
                Messagebox.show_warning("如果选择了inst.ini 文件 但是却没有选择driver 包的话 这样是不是build XML文件的",title="警告")
            # self.progressbar["value"] = 5
            # else:
            #     pass
            #
        else:
            Messagebox.ok(message='Driver CD Name 或者 XML Name 没有被定义')

    # 获取filelist 文件的信息
    def get_FileList_file_info(self, file):
        if os.path.exists(file):
            read_type = self.check_file_type(file)
            if read_type:
                filelist = []
                with open(file, "r", encoding=f'{read_type}') as fd:
                    while True:
                        line = fd.readline()
                        filelist.append(line)
                        if not line:
                            break
                if filelist:
                    return filelist
                else:
                    print("没有读取到文件")
                    return False
            else:
                print(f"{file}编码获取error 要检查一下")
        else:
            print("FileList文件不存在")
            return False

    def mount_file(self, Driver_path):
        # file = r"C:\Users\易守林\Desktop\X64W11_22H2_SWP_UX3404VA_00.02_Test2"
        # self.textbox_dcd.insert(END,
        #                         f"[{self.get_time()}] 文件复制fail {Driver_path}\inst.ini to {mount_file_name}\\I386\\inst.ini\n")
        if os.path.exists(Driver_path):
            os.chdir(Driver_path)
            mount_file_path = os.getcwd()
            mount_file_name = mount_file_path + "\mount"
            if os.path.exists(mount_file_name):
                # 判断文件是否存在，如果存在就要判断是否为空文件
                file_list = os.listdir(mount_file_name)
                if len(file_list) != 0:
                    # 提示文件不为空
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件不为空 请检查这个{mount_file_name}\n")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式退出\n")
                    # print(f"文件不为空 请检查这个{mount_file_name}")
                    # print("程式退出")
                    # sys.exit(0)
                    # return mount_file_name
                    # canshu = "discard"
                    # unmount_file(mount_file_name, canshu)

                    # file_name1 = r"C:\Users\易守林\Desktop\asd"
                    # file_name2 = r"C:\Users\易守林\Desktop\X64W11_22H2_SWP_UX3404VA_00.02_Test2\mount\FileList.txt"
                    # file_name3 = r"C:\Users\易守林\Desktop\X64W11_22H2_SWP_UX3404VA_00.02_Test2\mount\Software\Driver\DCH\Offline\ASUS\ASUS System Control Interface v3\3.1.5.0\14424"
                    # file_name4 = r"C:\Users\易守林\Desktop\X64W11_22H2_SWP_UX3404VA_00.02_Test2\mount\Software\Driver\DCH\Offline\ASUS\ASUS System Control Interface v3\3.1.5.0\14424"
                    #
                    # # 文件的删除
                    # shutil.rmtree(file_name3)
                    # # 文件的更改上一级别的目录名字
                    # file_name5 = file_name4.split("\\")
                    # file_name5.pop()
                    # file_name5 = "\\".join(file_name5)
                    # file_name6 = r"C:\Users\易守林\Desktop\X64W11_22H2_SWP_UX3404VA_00.02_Test2\mount\Software\Driver\DCH\Offline\ASUS\ASUS System Control Interface v3\3.5.5.0"
                    # os.rename(file_name5, file_name6)
                    # # 文件的创建
                    # file_name7 = r"C:\Users\易守林\Desktop\X64W11_22H2_SWP_UX3404VA_00.02_Test2\mount\Software\Driver\DCH\Offline\ASUS\ASUS System Control Interface v3\3.5.5.0\14424"
                    # os.mkdir(file_name7)
                    # # 文件的复制
                    # cmd = f'xcopy "{file_name1}\\*.*" "{file_name7}\\"  /y /e /s'
                    # print(cmd)
                    # (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                    # if status == 0:  # 返回值代表执行成功
                    #     print("文件复制成功")
                    #     print(uploadRes)
                    # else:
                    #     print(uploadRes)
                    # shutil.copy(f"{file_name1}", f"{file_name7}")

                    # # os.remove(file_name3)
                    # # os.rmdir(file_name3)
                    # # shutil.copy(f"{file_name1}",f"{file_name2}")
                    # # shutil.move(f"{file_name1}", f"{file_name2}")
                    # shutil.rmtree(file_name3)

                else:
                    Driver_cd_file = os.listdir(mount_file_path)
                    for i in Driver_cd_file:
                        # print(type(i))
                        chekc_item = "(.*.wim)"
                        if re.search(chekc_item, f"{i}"):
                            image_file = re.search(chekc_item, f"{i}")[0]
                            cmd = r"dism /cleanup-wim"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            self.textbox_dcd.see(END)
                            if status == 0:  # 返回值代表执行成功
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.textbox_dcd.see(END)
                                # time.sleep(2)
                                # print("aa")
                            cmd = "dism /Cleanup-Mountpoints"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            self.textbox_dcd.see(END)
                            if status == 0:  # 返回值代表执行成功
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.textbox_dcd.see(END)
                                # print("bb")
                                # time.sleep(2)
                            cmd = "dism /get-mountedwiminfo"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            self.textbox_dcd.see(END)
                            if status == 0:  # 返回值代表执行成功
                                # print("cc")
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.textbox_dcd.see(END)
                                # time.sleep(2)

                            cmd = f"dism /mount-image /imagefile:{image_file} /mountdir:{mount_file_name} /index:1 /CheckIntegrity"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            if status == 0:  # 返回值代表执行成功
                                # print(uploadRes)
                                print("文件已mount 出来")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件已mount 出来\n")
                                self.textbox_dcd.see(END)
                                return mount_file_name
                            else:
                                print("文件mount错误 需要在检查一下")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件mount错误 需要在检查一下\n")
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.progressbar_dcd.config(bootstyle="danger-striped")
                                self.progressbar_dcd_text_value.set(value="0%")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                self.textbox_dcd.see(END)
                                return False
            else:
                # 文件夹不存在需要创建
                os.mkdir(mount_file_name)
                if os.path.exists(mount_file_name):
                    Driver_cd_file = os.listdir(mount_file_path)
                    for i in Driver_cd_file:
                        # print(type(i))
                        chekc_item = "(.*.wim)"
                        if re.search(chekc_item, f"{i}"):
                            image_file = re.search(chekc_item, f"{i}")[0]
                            cmd = r"dism /cleanup-wim"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            self.textbox_dcd.see(END)
                            # self.textbox_dcd.insert(END, f"[{self.get_time()}] 选择的编译的XML文件是{path_xml}\n")
                            if status == 0:  # 返回值代表执行成功
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.textbox_dcd.see(END)
                                # time.sleep(4)
                                # print("aa")
                            cmd = "dism /Cleanup-Mountpoints"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            self.textbox_dcd.see(END)
                            if status == 0:  # 返回值代表执行成功
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.textbox_dcd.see(END)
                                # print("bb")
                                # time.sleep(4)
                            cmd = "dism /get-mountedwiminfo"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            self.textbox_dcd.see(END)
                            if status == 0:  # 返回值代表执行成功
                                # print("cc")
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.textbox_dcd.see(END)
                                # time.sleep(4)

                            cmd = f"dism /mount-image /imagefile:{image_file} /mountdir:{mount_file_name} /index:1 /CheckIntegrity"
                            (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                            print(f"执行程式{cmd}:")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式{cmd}:\n")
                            self.textbox_dcd.see(END)
                            if status == 0:  # 返回值代表执行成功
                                # print(uploadRes)
                                print("文件已mount 出来")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {image_file}文件已mount 出来\n")
                                self.textbox_dcd.see(END)
                                return mount_file_name
                            else:
                                print("文件mount错误 需要在检查一下")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {image_file}文件mount错误 需要在检查一下\n")
                                print(uploadRes)
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                                self.textbox_dcd.see(END)
                                self.progressbar_dcd.config(bootstyle="danger-striped")

                                self.progressbar_dcd_text_value.set(value="0%")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                return False
        else:
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有闯入Driver CD 具体的路径文件路径\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd_text_value.set(value="0%")
            return False
    def unmount_file(self, path, canshu):

        if canshu == "discard" or canshu == "commit":
            if os.path.exists(path):
                cmd = f'Dism /unmount-Image /MountDir:"{path}" /{canshu}'
                print(f"执行参数:{cmd}")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 开始执行程式{cmd}:\n")
                self.textbox_dcd.see(END)
                (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                if status == 0:  # 返回值代表执行成功
                    print("程式执行成功")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式执行成功:\n")
                    self.textbox_dcd.see(END)
                    # print(f"{cmd}")
                    return "PASS"
                else:
                    print("程式执行FAIL")
                    print(uploadRes)
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式执行FAIL {cmd}\n")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] {uploadRes}\n")
                    self.textbox_dcd.see(END)
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd_text_value.set(value="0%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                    return "FAIL"
            else:
                print(f"执行的文件不存在：{path}")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行的文件不存在：{path}\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd_text_value.set(value="0%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                return "FAIL"
        else:
            print(f"带入的参数有问题{canshu},不是我们要求的discard/commit")
            # return "FAIL"
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 带入的参数有问题{canshu},不是我们要求的discard/commit\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd_text_value.set(value="0%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            return "FAIL"

    def check_file_md5(self, filename):

        if os.path.exists(filename):
            md5_hash = hashlib.md5()
            with open(filename, "rb") as f:
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
                return md5_hash.hexdigest()
        else:
            print("文件路径有问题")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件路径有问题 {filename}\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd_text_value.set(value="0%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            return False
            # sys.exit(22)
            # print(md5_hash.hexdigest())

    def get_md5(self, filename):

        # filename = r"C:\Users\易守林\Desktop\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V101_for_PR\05.Intel_Graphics_31.0.101.3887"
        # filename2 = r"C:\Users\易守林\Desktop\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V101_for_PR\05.Intel_Graphics_31.0.101.388722"
        # c = checkmd5(filename)
        file_md5 = {}
        for root, dirs, files in os.walk(filename):
            for file in files:
                path = os.path.join(root, file)
                if os.path.exists(path):
                    if os.path.isfile(path):
                        try:
                            file_ma5_value = self.check_file_md5(path)
                        except:
                            print(f"get md5 fail{path}")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] get md5 fail{path}\n")
                            self.textbox_dcd.see(END)
                            self.progressbar_dcd.config(bootstyle="danger-striped")
                            self.progressbar_dcd_text_value.set(value="50%")
                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                            sys.exit(0)
                        else:
                            file_md5[f"{file}"] = file_ma5_value

        if file_md5:
            return file_md5
        else:
            self.textbox_dcd.insert(END, f"[{self.get_time()}] get md5 fail{filename}\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd_text_value.set(value="50%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            return False

    def copy_file(self, Driver_path,xml_file):
        # self.textbox_dcd.insert(END,
        #                         f"[{self.get_time()}]文件复制fail {Driver_path}\inst.ini to {mount_file_name}\\I386\\inst.ini\n")
        mount_file_name = self.mount_file(Driver_path)
        self.textbox_dcd.see(END)
        self.progressbar_dcd["value"] = 4
        self.progressbar_dcd_text_value.set(value="40%")
        if mount_file_name:
            if os.path.exists("inst1.ini"):
                os.remove("inst1.ini")
                print("文件已经删除：inst1.ini")
            elif os.path.exists("FileList1.txt"):
                print("文件已经删除：FileList1.txt")
                os.remove("FileList1.txt")
        else:
            self.textbox_dcd.insert(END, f"[{self.get_time()}] mount_file fail\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            Messagebox.show_error("mount_file_name 没有mount PASS")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            sys.exit(0)
        # 这里要修正一下 将修改driver CD 的name 等信息




        inst_file = f"{Driver_path}\\inst.ini"
        filelist_file = f"{mount_file_name}\FileList.txt"

        self.File_List = self.get_FileList_file_info(filelist_file)
        # 获取inst.ini 的文件信息
        self.inst_info = self.getinstinfo(inst_file)

        # 获取filelist.txt的信息以作修改
        self.File_List = self.get_FileList_file_info(filelist_file)
        # 获取inst.ini 的文件信息
        self.inst_info = self.getinstinfo(inst_file)
        # getxmlinfo, Driver_CD_Name = self.readXML(xml_file)
        if os.path.exists(xml_file):
            domTree = parse(f"{xml_file}")
            # 文档根元素
            rootNode = domTree.documentElement
            # print(rootNode.nodeName)
            customers = rootNode.getElementsByTagName("Part")
            getxmlinfo = {}
            Driver_CD_Name = ""
            for customer in customers:
                if customer.hasAttribute("Describ"):
                    if customer.hasAttribute("modid"):
                        Driver_CD_Name = customer.getAttribute("modid")
        else:
            Messagebox.show_error(f"{xml_file} 文件路径丢失")
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            sys.exit(0)

        # 修改inst.ini里面的 driver CD name
        for k2, v2 in self.inst_info.items():
            if k2 == "[FileList]":
                # 修改DCD_NAME
                v2["AsName"] = f"ReleaseNote_FileList of {Driver_CD_Name}\n"

        # 修改file_list 里面的 driver CD name
        for i in range(0, len(self.File_List)):
           if self.File_List[i].find("ReleaseNote_FileList of") != -1:
                self.File_List[i] = f"ReleaseNote_FileList of {Driver_CD_Name}\n"

        # 生成新的 ini 文件
        inst_file, filelist_file = self.build_to_inst_file(self.inst_info, self.File_List)


        if os.path.exists(f"{inst_file}") and os.path.exists(f"{filelist_file}"):
            self.progressbar_dcd["value"] = 5
            self.progressbar_dcd_text_value.set(value="50%")
            try:
                copyfile(f"{Driver_path}\\FileList1.txt",f"{mount_file_name}\FileList.txt")
                self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件复制PASS {Driver_path}\\FileList.txt to {mount_file_name}\FileList.txt\n")
                self.textbox_dcd.see(END)
            except:
                print(f"文件复制fail {Driver_path}\\FileList1.txt to {mount_file_name}\FileList.txt")
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd_text_value.set(value="50%")
                tkinter.messagebox.showinfo(title="copy file fail", message=f"文件复制fail {Driver_path}\\FileList1.txt to {mount_file_name}\FileList.txt")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件复制fail {Driver_path}\\FileList.txt to {mount_file_name}\FileList.txt\n")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                self.textbox_dcd.see(END)
                sys.exit(0)
            else:
                try:
                    copyfile(f"{Driver_path}\\inst1.ini", f"{mount_file_name}\\I386\\inst.ini")
                    self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件复制PASS {Driver_path}\inst.ini to {mount_file_name}\\I386\\inst.ini\n")
                    self.textbox_dcd.see(END)
                except:
                    print(f"文件复制fail {Driver_path}\inst1.ini to {mount_file_name}\\I386\\inst.ini")
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd_text_value.set(value="50%")
                    tkinter.messagebox.showinfo(title="copy file fail",message=f"文件复制fail {Driver_path}\inst1.ini to {mount_file_name}\\I386\\inst.ini")
                    self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件复制fail {Driver_path}\inst.ini1 to {mount_file_name}\\I386\\inst.ini\n")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                    self.textbox_dcd.see(END)
                    sys.exit(0)

            # 修改ASUS_SWP_UX3404VA.Ver VER文件
            self.progressbar_dcd["value"] = 6
            self.progressbar_dcd_text_value.set(value="60%")
            windows_path = f"{mount_file_name}\\Windows"
            c = os.listdir(windows_path)
            ck = "(.*\.Ver$)"
            for i in c:
                if re.findall(ck, i):
                    VER = re.findall(ck, i)[0]
                    read_type = self.check_file_type(f"{windows_path}\\{VER}")
                    with open(f"{windows_path}\\{VER}", "w", encoding=read_type) as file:
                        file.write(self.Driver_CD_Name)
            self.textbox_dcd.insert(END,f"[{self.get_time()}] 已经成功修改{windows_path}\\{VER}\n")

            # 移除MD5的文件和XLS文件
            self.progressbar_dcd["value"] = 7
            self.progressbar_dcd_text_value.set(value="70%")
            MD5 = os.listdir(f"{mount_file_name}")
            ck = "(.*\.md5$)"
            ck1 = "(.*\.xls$)"
            for i in MD5:
                if re.findall(ck, i):
                    MD5_name = re.findall(ck, i)[0]
                    os.remove(f"{mount_file_name}\\{MD5_name}")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功移除{mount_file_name}\\{MD5_name}\n")
                elif re.findall(ck1, i):
                    xls_name = re.findall(ck1, i)[0]
                    os.remove(f"{mount_file_name}\\{xls_name}")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功移除{mount_file_name}\\{xls_name}\n")

                # 移动xls 文件
            self.progressbar_dcd["value"] = 8
            self.progressbar_dcd_text_value.set(value="80%")
            MD51 = os.listdir(f"{Driver_path}")
            ck1 = "(.*\.xls$)"
            for i in MD51:
                if re.findall(ck1, i):
                    xls_name = re.findall(ck1, i)[0]
                    copyfile(xls_name, f"{mount_file_name}\\{xls_name}")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功复制{mount_file_name}\\{xls_name}\n")
            # 创建MD5值
            # os.chdir(DCD)
            # print(os.getcwd())


            if os.path.exists("fmd5x64.exe"):
                if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                    os.remove(f"{self.Driver_CD_Name}.md5")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功移除{self.Driver_CD_Name}.md5\n")
                else:
                    cmd = f"fmd5x64.exe -r -dmount>{self.Driver_CD_Name}.md5"
                    (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                    if status == 0:  # 返回值代表执行成功
                        if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                            md5_file = []
                            read_type = self.check_file_type(f"{self.Driver_CD_Name}.md5")
                            if read_type:
                                with open(f"{self.Driver_CD_Name}.md5", "r", encoding=f"{read_type}") as files:
                                    while True:
                                        line = files.readline()
                                        md5_file.append(line)
                                        if not line:
                                            break
                                os.remove(f"{self.Driver_CD_Name}.md5")
                                md5_file = md5_file[2:]
                                with open(f"{mount_file_name}\\{self.Driver_CD_Name}.md5", "w",
                                          encoding=f"{read_type}") as files:
                                    for line in md5_file:
                                        files.write(line)
                                if os.path.exists(f"{mount_file_name}\\{self.Driver_CD_Name}.md5"):
                                    print(f"文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5")
                                    self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5\n")
                    else:
                        self.textbox_dcd.insert(END,f"[{self.get_time()}] 执行程式FAIL {cmd}\n")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] FAIL的信息如下： {uploadRes}\n")
                        self.progressbar_dcd.config(bootstyle="danger-striped")
                        self.progressbar_dcd["value"] = 10
                        self.progressbar_dcd_text_value.set(value="100%")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                        self.textbox_dcd.see(END)
                        sys.exit(0)
            else:
                # C:\Users\Ben\Desktop\build_dcd
                # py_file = sys.argv[0]
                # os.path.dirname(py_file)
                # tool_path = str(os.path.dirname(py_file)) + "\\" + "fmd5x64.exe"
                # print("8888888888888888888888888888888")
                # print(tool_path)
                # print("8888888888888888888888888888888")
                tool_path = str(self.py_path) + "\\" + "fmd5x64.exe"
                if os.path.exists(tool_path):
                    copyfile(tool_path, f"{Driver_path}\\fmd5x64.exe")
                    if os.path.exists(f"{Driver_path}\\fmd5x64.exe"):
                        if os.path.exists("fmd5x64.exe"):
                            if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                                os.remove(f"{self.Driver_CD_Name}.md5")
                                self.textbox_dcd.insert(END,
                                                        f"[{self.get_time()}] 已经成功移除{self.Driver_CD_Name}.md5\n")
                                self.textbox_dcd.see(END)
                            else:
                                cmd = f"fmd5x64.exe -r -dmount>{self.Driver_CD_Name}.md5"
                                (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                                if status == 0:  # 返回值代表执行成功
                                    if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                                        md5_file = []
                                        read_type = self.check_file_type(f"{self.Driver_CD_Name}.md5")
                                        if read_type:
                                            with open(f"{self.Driver_CD_Name}.md5", "r",
                                                      encoding=f"{read_type}") as files:
                                                while True:
                                                    line = files.readline()
                                                    md5_file.append(line)
                                                    if not line:
                                                        break
                                            os.remove(f"{self.Driver_CD_Name}.md5")
                                            md5_file = md5_file[2:]
                                            with open(f"{mount_file_name}\\{self.Driver_CD_Name}.md5", "w",
                                                      encoding=f"{read_type}") as files:
                                                for line in md5_file:
                                                    files.write(line)
                                            if os.path.exists(f"{mount_file_name}\\{self.Driver_CD_Name}.md5"):
                                                print(f"文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5")
                                                self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] 文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5\n")
                                                self.textbox_dcd.see(END)
                                            else:
                                                print(f"文件不存在：{mount_file_name}\\{self.Driver_CD_Name}.md5")
                                                self.progressbar_dcd.config(bootstyle="danger-striped")
                                                self.progressbar_dcd["value"] = 10
                                                self.progressbar_dcd_text_value.set(value="100%")
                                                self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] 文件不存在：{mount_file_name}\\{self.Driver_CD_Name}.md5\n")
                                                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                                self.textbox_dcd.see(END)
                                                sys.exit(0)
                                        else:
                                            print(f"{self.Driver_CD_Name}.md5 的编码获取失败 请检查一下")
                                            self.progressbar_dcd.config(bootstyle="danger-striped")
                                            self.progressbar_dcd["value"] = 10
                                            self.progressbar_dcd_text_value.set(value="100%")
                                            self.textbox_dcd.insert(END,
                                                                    f"[{self.get_time()}]{self.Driver_CD_Name}.md5 的编码获取失败 请检查一下\n")
                                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                            self.textbox_dcd.see(END)
                                            sys.exit(0)

                                    else:
                                        print(f"{self.Driver_CD_Name}.md5 不存在")
                                        self.progressbar_dcd.config(bootstyle="danger-striped")
                                        self.progressbar_dcd["value"] = 10
                                        self.progressbar_dcd_text_value.set(value="100%")
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] {self.Driver_CD_Name}.md5 不存在\n")
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                        self.textbox_dcd.see(END)
                                        sys.exit(0)

                                else:
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行程式FAIL {cmd}\n")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] FAIL的信息如下： {uploadRes}\n")
                                    self.progressbar_dcd.config(bootstyle="danger-striped")
                                    self.progressbar_dcd["value"] = 10
                                    self.progressbar_dcd_text_value.set(value="100%")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                    self.textbox_dcd.see(END)
                                    sys.exit(0)
                    else:
                        print("fmd5x64.exe 工具不存在")
                        self.progressbar_dcd.config(bootstyle="danger-striped")
                        self.progressbar_dcd["value"] = 10
                        self.progressbar_dcd_text_value.set(value="100%")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有再这个路径发现{Driver_path}\\fmd5x64.exe\n")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                        self.textbox_dcd.see(END)
                        # Messagebox.show_error("没有再这个路径发现{Driver_path}\\fmd5x64.exe", title="fmd5x64.exe 工具不存在")
                        # sys.exit(0)
                else:
                    print("fmd5x64.exe 工具不存在")
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有再这个路径发现{tool_path}\n")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                    self.textbox_dcd.see(END)
                    # Messagebox.show_error("没有再这个路径发现{Driver_path}\\fmd5x64.exe",
                    #                       title="fmd5x64.exe 工具不存在")
                    # sys.exit(0)

            canshu = "commit"
            self.unmount_file(mount_file_name, canshu)
            # time.sleep(1)
            # os.remove("mount")

            # CHECK MD5 值
            filename = f"{Driver_path}\\Driver64.wim"
            self.progressbar_dcd["value"] = 9
            self.progressbar_dcd_text_value.set(value="90%")
            def checkmd5(filename):

                if os.path.exists(filename):
                    md5_hash = hashlib.md5()
                    with open(filename, "rb") as f:
                        # Read and update hash in chunks of 4K
                        for byte_block in iter(lambda: f.read(4096), b""):
                            md5_hash.update(byte_block)
                        return md5_hash.hexdigest()
                else:
                    print(f"{filename}文件路径有问题,导致无法得出他的MD5值")
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] {filename}文件路径有问题,导致无法得出他的MD5值\n")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                    self.textbox_dcd.see(END)
                    # sys.exit(0)
                    return False
                    # sys.exit(22)
                    # print(md5_hash.hexdigest())

            print("开始检查MD5值")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 开始检查MD5值\n")
            self.textbox_dcd.see(END)
            if checkmd5(filename):
                md5_num = checkmd5(filename).upper()
                file_MD5 = f"{Driver_path}\\Driver64.md5"
                read_type = self.check_file_type(f"{file_MD5}")
                with open(file_MD5, "w", encoding=read_type) as fd:
                    fd.write(md5_num)
                print("DCD Build PASS")
                tkinter.messagebox.showinfo(title="DCD Build PASS", message=f"{self.Driver_CD_Name} Build PASS")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] {self.Driver_CD_Name} Driver CD Build PASS\n")

                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
            else:
                print("MD5 FAIL")
                Messagebox.show_error("MD5 FAIL", title="Error")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] {self.Driver_CD_Name} MD5 FAIL\n")
                self.textbox_dcd.see(END)

        else:
            print(f'文件不存在{inst_file}，{filelist_file}')
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            Messagebox.show_error(f'文件不存在{inst_file}，{filelist_file}', title="Error")
            sys.exit(0)

    def build_to_inst_file(self, inst_info, File_List):
        # 现在经得到的JSON
        # 文件生成新的inst.ini文件
        # 然后比较两个文件的不同
        if File_List != "NA":
            os.getcwd()
            if inst_info:
                with open("inst1.ini", "w", encoding="utf-16") as fp:
                    for k1, v1 in inst_info.items():
                        fp.write(f"{k1}\n")
                        for kk1, vv1 in v1.items():
                            if f"{kk1}" == f"{vv1}" and f"{kk1}" == "\n" and f"{vv1}" == "\n":
                                fp.write("\n")
                            elif f"{kk1}" == f"{vv1}" and f"{kk1}" != "\n":
                                fp.write(f"{vv1}")
                            else:
                                fp.write(f"{kk1}={vv1}")
                            # 考虑到两个stage 至之间至少有两个空行
                        fp.write("\n")
            else:
                print("传入的文件不存在 inst1.ini build fail")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 传入的文件不存在 inst1.ini build fail\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                sys.exit(0)
            if File_List:
                with open("FileList1.txt", "w", encoding="utf-8") as fp:
                    for i in File_List:
                        fp.write(i)
            else:
                print("传入的文件不存在 FileList1.tx build fail")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 传入的文件不存在 inst1.ini build fail\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                sys.exit(0)

            if os.path.exists("inst1.ini"):
                if os.path.exists("FileList1.txt"):
                    return "inst1.ini", "FileList1.txt"
            else:
                self.textbox_dcd.insert(END, f"[{self.get_time()}] inst1.ini & FileList1.txt 两个文件没有生成\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                return False
        else:
            os.getcwd()
            if inst_info:
                with open("inst1.ini", "w", encoding="utf-16") as fp:
                    for k1, v1 in inst_info.items():
                        fp.write(f"{k1}\n")
                        for kk1, vv1 in v1.items():
                            if f"{kk1}" == f"{vv1}" and f"{kk1}" == "\n" and f"{vv1}" == "\n":
                                fp.write("\n")
                            elif f"{kk1}" == f"{vv1}" and f"{kk1}" != "\n":
                                fp.write(f"{vv1}")
                            else:
                                fp.write(f"{kk1}={vv1}")
                            # 考虑到两个stage 至之间至少有两个空行
                        fp.write("\n")
            else:
                print("传入的文件不存在 inst1.ini build fail")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 传入的文件不存在 inst1.ini build fail\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                # sys.exit(0)

            if os.path.exists("inst1.ini"):
                return "inst1.ini"
            else:
                self.textbox_dcd.insert(END, f"[{self.get_time()}] inst1.ini两个文件没有生成\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                return False

    def compart_file_md5(self, filename1, filename2):
        # filename = r"C:\Users\易守林\Desktop\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V101_for_PR\05.Intel_Graphics_31.0.101.3887"
        # filename2 = r"C:\Users\易守林\Desktop\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V101_for_PR\05.Intel_Graphics_31.0.101.388722"

        fail_list = []
        file_md51 = self.get_md5(filename1)
        file_md52 = self.get_md5(filename2)
        for k, v in file_md51.items():
            if k in file_md52.keys():
                if file_md51[k] == file_md52[k]:
                    # print(f"文件比对PASS：{k}，{file_md51[k]} == {file_md52[k]}")
                    # fail_list.append(f"文件比对PASS：{k}，{file_md51[k]} == {file_md52[k]}")
                    continue
                else:
                    print(f'文件比对FAIL{k},{file_md51[k]} != {file_md52[k]}')
                    fail_list.append(f'文件比对FAIL{k},{file_md51[k]} != {file_md52[k]}')
            else:
                print(f'文件不存在{k}')
        if len(fail_list) == 0:
            return "PASS"
        else:
            return False

    def readXML(self, file):
        os.getcwd()
        # file = r"confi2.xml"
        # file = r"cc.xml"
        if os.path.exists(file):
            domTree = parse(f"{file}")
            # 文档根元素
            rootNode = domTree.documentElement
            # print(rootNode.nodeName)
            customers = rootNode.getElementsByTagName("Part")
            getxmlinfo = {}
            Driver_CD_Name = ""
            for customer in customers:
                if customer.hasAttribute("Describ"):
                    # print(customer.getAttribute("Describ"))
                    if customer.getAttribute("Describ") != "ADDCOMMENT":
                        if customer.hasAttribute("Stage"):
                            Stage = customer.getAttribute("Stage")
                            getxmlinfo[f"{Stage}"] = {}
                            # if customer.hasAttribute("Stage"):
                            #     getxmlinfo[f"{name}"]["Stage"] = customer.getAttribute("Stage")
                            if customer.hasAttribute("Date"):
                                getxmlinfo[f"{Stage}"]["Date"] = customer.getAttribute("Date")
                            if customer.hasAttribute("version"):
                                getxmlinfo[f"{Stage}"]["version"] = customer.getAttribute("version")
                            if customer.hasAttribute("FilePath"):
                                getxmlinfo[f"{Stage}"]["FilePath"] = customer.getAttribute("FilePath")
                            if customer.hasAttribute("HWID"):
                                getxmlinfo[f"{Stage}"]["HWID"] = customer.getAttribute("HWID")
                            if customer.hasAttribute("Type"):
                                getxmlinfo[f"{Stage}"]["Type"] = customer.getAttribute("Type")
                        if customer.hasAttribute("modid"):
                            Driver_CD_Name = customer.getAttribute("modid")
                    else:
                        # print("sdscsddsdvdfvdv")
                        if customer.hasAttribute("targer"):
                            targer = customer.getAttribute("targer")
                            getxmlinfo[f"{targer}"] = {}
                            if customer.hasAttribute("commentinfo"):
                                getxmlinfo[f"{targer}"]["commentinfo"] = customer.getAttribute("commentinfo")
        else:
            print("文件不存在")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] xml文件不存在\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            # sys.exit(0)
            # return False
        if Driver_CD_Name:
            if getxmlinfo:
                # print("PASS")
                # # getxmlinfo, Driver_CD_Name = readXML()
                # print("修改信息展示：")
                # for k, v in getxmlinfo.items():
                #     print(k)
                #     for k1, v1 in v.items():
                #         print(f"{k1}:{v1}")
                # print(Driver_CD_Name)
                return getxmlinfo, Driver_CD_Name
            else:
                print("获取修改信息有误 检查XML文档")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 获取修改信息有误 检查XML文档\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                return False
        else:
            print("未定义Driver CD Name")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 未定义Driver CD Name\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            return False

    def add_Comment(self, Driver_path, Driver_CD_Name, getxmlinfo, mount_file_name):
        # 该函数主要是确定增加的组件并将其合入到指定的组件中去
        # 这里有几个逻辑 如果新增的组件编
        os.chdir(Driver_path)
        mount_file_path = os.getcwd()
        # mount_file_name = mount_file_path + "\mount"
        # Driver_CD_Name = "X64W11_22H2_SWP_UX3402VA_01.02_TEST_for_cortana"
        file_inst = f"{Driver_path}\\inst1.ini"
        targer_num = "NA"
        file_New_coment = ""
        for k,v in getxmlinfo.items():
            for kk,vv in v.items():
                if kk == "commentinfo":
                    targer_num = k
                    file_New_coment = vv

        # file_New_coment = f"{Driver_path}\\NewComment.ini"
        # print("开始增加组件")
        if os.path.exists(file_New_coment):
            # print("fuck  fuck fuck")
            # 修改inst.ini 文件
            items = self.getinstinfo(file_inst)
            items1 = self.getinstinfo(file_New_coment)
            self.inst_info = {}
            new_comment_name = list(items1.keys())[0]
            # print(f"新增加的组件是是{new_comment_name}")
            #
            for k, v in items.items():
                if k.find("[Stage") != -1:
                    if len(items1.keys()) == 1:
                        if new_comment_name in items.keys():
                            if new_comment_name == k:
                                self.inst_info[k] = items1[k]
                                k1 = f"{k.split(' ')[0]} " + f"{str(int(k.split(' ')[1].strip(']')) + 1)}]"
                                # print("xxxxxxxxxx")
                                # print(k1)
                                # print("xxxxxxxxxx")
                                if k1 not in items.keys():
                                    self.inst_info[k1] = items[k]
                                    # print(self.inst_info[k1])
                                    # print("aaaaaaaaaaaaaaa")
                                    continue
                                else:
                                    print("组件编号冲突")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 新增组件版号冲突\n")
                                    self.textbox_dcd.see(END)
                                    self.progressbar_dcd.config(bootstyle="danger-striped")
                                    self.progressbar_dcd["value"] = 10
                                    self.progressbar_dcd_text_value.set(value="100%")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                    sys.exit(0)
                        else:
                            if targer_num != "NA":
                                if k == targer_num:
                                    self.inst_info[new_comment_name] = items1[new_comment_name]
                                    self.inst_info[k] = items[k]
                                    continue
                                else:
                                    self.inst_info[k] = items[k]
                                    continue
                            else:
                                self.inst_info[k] = items[k]
                                continue
                    self.inst_info[k] = items[k]
                    continue
                else:
                    self.inst_info[k] = items[k]

            # mount_file_name = mount_file(Driver_path)
            # 这是实验的数据 后期可能会直接删除掉
            if mount_file_name:
                if os.path.exists("inst1.ini"):
                    os.remove("inst1.ini")
                    print("文件已经删除：inst1.ini")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件已经删除：inst1.ini\n")
                    self.textbox_dcd.see(END)
                elif os.path.exists("FileList1.txt"):
                    print("文件已经删除：FileList1.txt")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件已经删除：FileList1.txt\n")
                    self.textbox_dcd.see(END)
                    os.remove("FileList1.txt")
                for k2, v2 in self.inst_info.items():
                    if k2 == "[FileList]":
                        # 修改DCD_NAME
                        v2["AsName"] = f"ReleaseNote_FileList of {Driver_CD_Name}\n"
                    if k2 == new_comment_name:
                        # 先删除文件在复制文件 在修改名字
                        Softwar_path = self.inst_info[k2]["AsDir"].strip("\n")
                        # AsName=Driver\DCH\Offline\I2C\Intel\I2C_DCH\30.100.2221.20\30111
                        # 确定之前旧版本的文件路径
                        inst_file_path = f"{mount_file_name}\\{Softwar_path}\\{self.inst_info[k2]['AsName']}"
                        inst_file_path = inst_file_path.strip("\n")
                        if os.path.exists(inst_file_path):
                            try:
                                shutil.rmtree(inst_file_path)
                            except FileNotFoundError as e:
                                print(e)
                            finally:
                                if os.path.exists(inst_file_path):
                                    cmd = f"RD /s /q \\\?\\\"{inst_file_path}\""
                                    (status, uploadRes) = subprocess.getstatusoutput(cmd)
                                    if status == 0:  # 返回值代表执行成功
                                        # print(uploadRes)
                                        print(f"用批处理指令RD 删除文件{inst_file_path}")
                                        self.textbox_dcd.insert(END, f"[ 用批处理指令RD 删除文件{inst_file_path}\n")
                                        self.textbox_dcd.see(END)
                                        time.sleep(2)
                                    else:
                                        print("fail")
                                        print(uploadRes)
                                        self.textbox_dcd.insert(END,
                                                                f"[{self.get_time()}] {inst_file_path}执行程式{cmd}\n{uploadRes}fail\n")
                                        self.textbox_dcd.see(END)
                                        # sys.exit(0)
                                else:
                                    print(f"{inst_file_path}文件不存在 可能已经被删除了")
                                    print(f"开始执行下一步骤文件的复制")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] {inst_file_path}文件不存在 可能已经被删除了\n")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 开始执行下一步骤文件的复制\n")
                                    self.textbox_dcd.see(END)
                            if os.path.exists(inst_file_path):
                                print("文件未删除删除")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {inst_file_path}文件未删除删除{inst_file_path}\n")
                                self.textbox_dcd.see(END)
                                # sys.exit(0)
                            else:
                                os.makedirs(inst_file_path)
                                print(f"{new_comment_name}：{inst_file_path}文件已经创建，开始复制文件")
                                self.textbox_dcd.insert(END, f"[{self.get_time()}] {inst_file_path}{new_comment_name}：{inst_file_path}文件已经创建，开始复制文件\n")
                                self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件存在，开始去复制到新的路径中去\n")
                                print("文件存在，开始去复制到新的路径中去")
                                self.textbox_dcd.see(END)
                                source_file = self.inst_info[k2]["FilePath"].strip("\n")
                                cmd = f'Robocopy "{source_file}" "{inst_file_path}" /E /R:2'
                                time.sleep(1)
                                # print(cmd)
                                (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                                if status == 1:  # 返回值代表执行成功
                                    print("文件复制完成开始比较文件的MD5值")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] {cmd}文件复制完成开始比较文件的MD5值\n")
                                    self.textbox_dcd.see(END)
                                    resuit = self.compart_file_md5(source_file, inst_file_path)
                                    if not resuit:
                                        print("文件复制FAIL MD5 check FAIL ")
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件复制FAIL MD5 check FAIL\n")
                                        # print(cmd)
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件复制FAIL MD5 check FAIL{cmd}\n")
                                        self.textbox_dcd.see(END)
                                        # sys.exit(0)
                                    else:
                                        print("文件复制PASS MD5 check PASS ")
                                        self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件复制PASS MD5 check PASS\n")
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 新增组件添加完成\n")
                                        print("新增组件添加完成")
                                        self.textbox_dcd.see(END)
                                    # print(uploadRes)
                                else:
                                    print(uploadRes)
                                    print("执行程式异常终止")
                                    print(status)
                                    print(f"{cmd}")

                        else:
                            os.makedirs(inst_file_path)
                            if os.path.exists(inst_file_path):
                                if os.path.exists(inst_file_path):
                                    print(f"{new_comment_name}：{inst_file_path}文件已经创建，开始复制文件")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] {new_comment_name}：{inst_file_path}文件已经创建，开始复制文件\n")
                                    self.textbox_dcd.see(END)
                                    print("文件存在，开始去复制到新的路径中去")
                                    self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件存在，开始去复制到新的路径中去\n")
                                    self.textbox_dcd.see(END)
                                    source_file = self.inst_info[k2]["FilePath"].strip("\n")
                                    cmd = f'Robocopy "{source_file}" "{inst_file_path}" /E /R:2'
                                    # print("文件复制完成开始比较文件的MD5值")
                                    # resuit = self.compart_file_md5(inst_file_path_new, FilePath)
                                    # if not resuit:
                                    #     print("文件复制FAIL MD5 check FAIL ")
                                    #     print(cmd)
                                    #     sys.exit(0)
                                    # else:
                                    #     print("文件复制PASS MD5 check PASS ")
                                    time.sleep(1)
                                    # print(cmd)
                                    (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                                    if status == 1:  # 返回值代表执行成功
                                        print("文件复制完成开始比较文件的MD5值")
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件复制完成开始比较文件的MD5值\n")
                                        resuit = self.compart_file_md5(source_file, inst_file_path)
                                        if not resuit:
                                            print("文件复制FAIL MD5 check FAIL ")
                                            self.textbox_dcd.insert(END, f"[{self.get_time()}] {cmd}文件复制FAIL MD5 check FAIL\n")
                                            self.textbox_dcd.see(END)
                                            # print(cmd)
                                            # sys.exit(0)
                                        else:
                                            print("文件复制PASS MD5 check PASS ")
                                            print("新增组件添加完成")
                                            self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件复制PASS MD5 check PASS\n")
                                            self.textbox_dcd.insert(END,
                                                                    f"[{self.get_time()}] 新增组件添加完成\n")
                                            self.textbox_dcd.see(END)
                                        # print(uploadRes)
                                    else:
                                        print(uploadRes)
                                        print("执行程式异常终止")
                                        print(status)
                                        print(f"{cmd}")
                                        self.progressbar_dcd.config(bootstyle="danger-stripe")
                                        self.progressbar_dcd["value"] = 10
                                        self.progressbar_dcd_text_value.set(value="100%")
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 执行的指令是{cmd}\n")
                                        self.textbox_dcd.insert(END,
                                                                f"[{self.get_time()}] 执行的指令结果{status}\n")
                                        self.textbox_dcd.see(END)

                                        # sys.exit(0)
                                else:
                                    print(f"该文件不存在{inst_file_path}")
                                    Messagebox.show_error(f"该文件不存在{inst_file_path}", title="Error")
                                    print("需要检擦 后期将记录在LOG文件中去")
            else:
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 'mount DCD FAIL '\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                # sys.exit(0)


        else:
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有定义{file_New_coment}\n")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            self.textbox_dcd.see(END)
            # sys.exit(0)
                # # =======================================================================
                # File_List = "NA"
                # if inst_info and File_List:
                #     # "inst1.ini", "FileList1.txt"
                #     inst_file = build_to_inst_file(inst_info, File_List)
                #     # 文件的的复制
                #     if os.path.exists(f"{inst_file}"):
                #         try:
                #             copyfile(f"{Driver_path}\\inst1.ini", f"{mount_file_name}\\I386\\inst.ini")
                #         except:
                #             print(f"文件复制fail {Driver_path}\inst1.ini to {mount_file_name}\\I386\\inst.ini")
                #             sys.exit(0)
                #     else:
                #         print(f'文件不存在{inst_file}')
                #         sys.exit(0)

    def main_build(self, Driver_path, xml_file ):
        os.chdir(Driver_path)
        inst_file = r"inst.ini"
        FileList = r"FileList.txt"
        # xml_file = "new.xml"
        # 获取filelist.txt的信息以作修改
        File_List = self.get_FileList_file_info(FileList)
        # 获取inst.ini 的文件信息
        self.inst_info = self.getinstinfo(inst_file)
        # 获取xml文件里面的信息
        getxmlinfo, Driver_CD_Name = self.readXML(xml_file)
        # mount wim
        mount_file_name = self.mount_file(Driver_path)
        file_list = os.listdir(mount_file_name)
        # print(file_list)
        if len(file_list) != 0:
            pass
        else:
            Messagebox.show_error(f"mount 文件为空，请检查是否没有正确的mount")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] mount FAIL {mount_file_name}\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            # time.sleep(1)
            sys.exit(0)
        self.progressbar_dcd["value"] = 4
        self.progressbar_dcd_text_value.set(value="40%")
        # 这是实验的数据 后期可能会直接删除掉
        if mount_file_name:
            if os.path.exists("inst1.ini"):
                os.remove("inst1.ini")
                print("文件已经删除：inst1.ini")
            elif os.path.exists("FileList1.txt"):
                print("文件已经删除：FileList1.txt")
                os.remove("FileList1.txt")


            # 修改DCD_NAME
            # for k, v in inst_info.items():
            #     if k == "[FileList]":
            #         # 修改DCD_NAME
            #         v["AsName"] = f"ReleaseNote_FileList of {Driver_CD_Name}\n"
            #         print(v)
            #         break
            # 修改inst.ini里面的字典里面的数据 根据XML文档
            """
            {'[Stage 64]': {'Date': '07-18-1968', 'version': '10.1.36.7', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA  -VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\01.Intel_Chipset_10.1.36.7', 'HWID': '', 'Type': ''}, 
            '[Stage 62]': {'Date': ' 05-17-2022', 'version': '30.100.2221.20', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\02_1.Intel_SerialIO_I2C_30.100.2221.20', 'HWID': '', 'Type': ''}, 
            '[Stage 60]': {'Date': ' 05-17-2022', 'version': '30.100.2221.20', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\02_4.Intel_SerialIO_GPIO_30.100.2221.20', 'HWID': '', 'Type': ''}, 
            '[Stage 66]': {'Date': ' 09-30-2022', 'version': '2240.3.4.0', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\03.Intel_ME_2240.3.4.0', 'HWID': '', 'Type': ''}, 
            '[Stage 86]': {'Date': ' 09-14-2022', 'version': '1.0.11100.29710', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\04.Intel_DPTF_1.0.11100.29710', 'HWID': '', 'Type': ''}, 
            '[Stage 78]': {'version': '1.100.3408.0', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\05_1.Intel_IGCC_1.100.3408.0'}, '[Stage 104]': {'Date': ' 01-21-2022', 'version': '2.2.2.1', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\06.Intel_HID_Driver_2.2.2.1', 'HWID': '', 'Type': ''}, 
            '[Stage 70]': {'Date': ' 09-02-2022', 'version': '3.1.0.4586', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\08.Intel_ISH_3.1.0.4586', 'HWID': '', 'Type': ''}, '[Stage 68]': {'Date': '08-25-2022', 'version': '19.5.1.1040', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\09.Intel_VMD_19.5.1.1040', 'HWID': '', 'Type': ''}, 
            '[Stage 82]': {'Date': ' 11-02-2022', 'version': '6.0.9435.1', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\11.RTK_Codec_6.0.9435.1', 'HWID': '', 'Type': ''}, '[Stage 158]': {'version': '1.39.283.0', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\11_1.Rtk_Audio_UWP_1.39.283.0'}, 
            '[Stage 106]': {'Date': ' 11-08-2022', 'version': '7.1109.1132.19', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\12.Dolby_APO_7.1109.1132.19', 'HWID': '', 'Type': ''}, '[Stage 90]': {'Date': ' 09-23-2022', 'version': '22.180.0.2', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\13_1.Intel_BT_AX211_22.180.0.2', 'HWID': '', 'Type': ''}, 
            '[Stage 88]': {'Date': ' 10-27-2022', 'version': '1.930.0.251', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\14_1.MTK_BT_MTK7922_1.930.0.251', 'HWID': '', 'Type': ''}, '[Stage 98]': {'version': '1153.9.823.2022', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\15.RTK_LAN_Dongle_1153.9.823.2022'}, 
            '[Stage 76]': {'Date': ' 11-06-2022', 'version': '31.0.15.2678', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\16.NVIDIA_GFX_31.0.15.2678', 'HWID': '', 'Type': ''}, 
            '[Stage 80]': {'version': '8.1.962.0', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\16_1.NVIDIA_NVCC_8.1.962.0'}, '[Stage 100]': {'Date': ' 05-31-2022', 'version': '16.0.0.13', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\17.Touchpad_16.0.0.13', 'HWID': '', 'Type': ''}, '[Stage 102]': {'Date': ' 06-10-2022', 'version': '17.0.0.10', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\18.Numberpad_17.0.0.10', 'HWID': '', 'Type': ''}, 
            '[Stage 152]': {'Date': ' 11-02-2022', 'version': '1.0.4.0', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\19.Morpho_AI_Camera_1.0.4.0', 'HWID': '', 'Type': ''}, '[Stage 94]': {'Date': ' 08-31-2022', 'version': '2.1022.831.5', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\20.Intel_ICPS_2.1022.831.5', 'HWID': '', 'Type': ''}, 
            '[Stage 110]': {'version': '2.1022.831.0', 'FilePath': 'C:\\Users\\易守林\\Desktop\\UX3404VA-VC_NB6371A-B_Driver_List_Win11_22H2_V100_for_PR\\20_1.Intel_ICPS_UWP_2.1022.831.0'}}

            """
        else:
            self.textbox_dcd.insert(END, f"[{self.get_time()}] mount FAIL {mount_file_name}\n")
            self.textbox_dcd.see(END)
            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            sys.exit(0)

        self.progressbar_dcd["value"] = 5
        self.progressbar_dcd_text_value.set(value="50%")
        for k1, v1 in getxmlinfo.items():
            print(k1, v1)
            # if "commentinfo" not in v1.keys():
            if len(v1.keys()) == 1 and list(v1.keys())[0] == "commentinfo":
                # 先去创建一个inst1.ini
                inst_file, filelist_file = self.build_to_inst_file(self.inst_info, File_List)
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 开始去增加新的组件\n")
                self.textbox_dcd.see(END)
                self.add_Comment(Driver_path, Driver_CD_Name, getxmlinfo, mount_file_name)

            else:
                for k2, v2 in self.inst_info.items():
                    if k2 == "[FileList]":
                        # 修改DCD_NAME
                        v2["AsName"] = f"ReleaseNote_FileList of {Driver_CD_Name}\n"
                    # 确定两个stage 相同
                    if k1 == k2:
                        print("ssssss")
                        print(k2)
                        print("ssssss")
                        # inst里面的版本和日期的修改
                        date_time = ""
                        version = v2["DisplayVersion"][1:].strip("\n")
                        # 这里主要是将filelist txt 进行更改
                        for i in range(0, len(File_List)):
                            if File_List[i].find(f"{version}") != -1:
                                File_List[i] = File_List[i].replace(version, v1["version"])
                            elif File_List[i].find("ReleaseNote_FileList of") != -1:
                                File_List[i] = f"ReleaseNote_FileList of {Driver_CD_Name}\n"
                        try:
                            # 这是为了防止非Driver 的组件 没有日期说法一说
                            date_time = v2["Date_1"].strip("\n")
                        except:
                            pass
                        finally:
                            if not date_time:
                                date_time = "NA"
                        # for kk1, vv1 in v1.items():
                        for kk2, vv2 in v2.items():
                            # 这是修改version 这是一个坑
                            # if vv2.find(f"{version}") != -1:
                            if kk2 == "AsName":
                                # 先删除文件在复制文件 在修改名字
                                Softwar_path = self.inst_info[k2]["AsDir"].strip("\n")
                                # AsName=Driver\DCH\Offline\I2C\Intel\I2C_DCH\30.100.2221.20\30111
                                # 确定之前旧版本的文件路径
                                inst_file_path = f"{mount_file_name}\\{Softwar_path}\\{self.inst_info[k2][kk2]}"
                                # 删除最后一个文件夹的文件
                                inst_file_path_list = inst_file_path.split("\\")[:-1]
                                asname_version = inst_file_path_list[-1].strip("\n").strip(" ").strip("")
                                # 这里将会返回一个列表的数值
                                # AsName=Driver\DCH\Offline\I2C\Intel\I2C_DCH\30.100.2221.20
                                # 将文件再完整的串起来
                                inst_file_path = "\\".join(inst_file_path_list)
                                # 判断文件是存在 如果存在就删除该文件及以下的文件资料
                                if os.path.exists(inst_file_path):
                                    try:
                                        shutil.rmtree(inst_file_path)
                                    except FileNotFoundError as e:
                                        print(e)
                                    finally:
                                        if os.path.exists(inst_file_path):
                                            cmd = f"RD /s /q \\\?\\\"{inst_file_path}\""
                                            (status, uploadRes) = subprocess.getstatusoutput(cmd)
                                            if status == 0:  # 返回值代表执行成功
                                                # print(uploadRes)
                                                print(f"用批处理指令RD 删除文件{inst_file_path}")
                                                self.textbox_dcd.insert(END,f"[{self.get_time()}] 用批处理指令RD 删除文件{inst_file_path}\n")
                                                self.textbox_dcd.see(END)
                                                time.sleep(2)
                                            else:
                                                self.progressbar_dcd.config(bootstyle="danger-striped")
                                                self.textbox_dcd.insert(END,
                                                                            f"[{self.get_time()}] fail\n")
                                                self.textbox_dcd.insert(END,
                                                                            f"[{self.get_time()}] 用批处理指令RD 删除文件{inst_file_path}\n")
                                                self.textbox_dcd.insert(END, f"[{self.get_time()}]执行的指令是{cmd}\n")
                                                print(uploadRes)
                                                self.textbox_dcd.insert(END,f"[{self.get_time()}] {uploadRes}\n")
                                                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                                self.textbox_dcd.see(END)
                                                sys.exit(0)
                                        else:
                                            print(f"{inst_file_path}文件不存在 可能已经被删除了")
                                            self.textbox_dcd.insert(END, f"[{self.get_time()}] {inst_file_path}文件不存在 可能已经被删除了\n")
                                            self.textbox_dcd.see(END)
                                            self.textbox_dcd.see(END)
                                            print(f"开始执行下一步骤文件的复制")
                                            self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] {inst_file_path}开始执行下一步骤文件的复制\n")
                                            self.textbox_dcd.see(END)
                                else:
                                    print(f"{inst_file_path}文件不存在 可能已经被删除了")
                                    self.textbox_dcd.insert(END,f"[{self.get_time()}] {inst_file_path}文件不存在 可能已经被删除了\n")
                                    self.textbox_dcd.see(END)
                                    print(f"开始执行下一步骤文件的复制")
                                    self.textbox_dcd.insert(END,
                                                                f"[{self.get_time()}] 开始执行下一步骤文件的复制\n")
                                    self.textbox_dcd.see(END)
                                    # 然后修改inst.ini里面的版本号
                                self.inst_info[k2][kk2] = vv2.replace(asname_version, v1["version"])
                                # print(f"{self.inst_info[k2][kk2]}版本已经修改{version}==>{v1['version']}")




                                # 确定新的文件路径的位置 准备替换文件中
                                inst_file_path_new = f"{mount_file_name}\\{Softwar_path}\\{self.inst_info[k2][kk2]}"
                                inst_file_path_new = inst_file_path_new.strip("\n")
                                if not os.path.exists(inst_file_path_new):
                                    try:
                                        os.makedirs(inst_file_path_new)
                                    except:
                                        print(f"{inst_file_path_new}文件创建fail")
                                        Messagebox.show_error(f"{inst_file_path_new}文件创建fail", title="Error")
                                        self.textbox_dcd.insert(END,
                                                                    f"[{self.get_time()}] {inst_file_path_new}文件创建fail\n")
                                        self.textbox_dcd.see(END)
                                        self.progressbar_dcd.config(bootstyle="danger-striped")
                                        self.progressbar_dcd["value"] = 10
                                        self.progressbar_dcd_text_value.set(value="100%")
                                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                        sys.exit(0)
                                    else:
                                        print(f"{inst_file_path_new}文件创建PASS，开始复制文件")
                                        self.textbox_dcd.insert(END,
                                                                    f"[{self.get_time()}] {inst_file_path_new}文件创建PASS，开始复制文件\n")
                                        self.textbox_dcd.see(END)
                                        # f"{inst_file_path_new}文件创建fail"
                                else:
                                    try:
                                        shutil.rmtree(inst_file_path_new)
                                    except FileNotFoundError as e:
                                        print(e)
                                    finally:
                                        if os.path.exists(inst_file_path_new):
                                            cmd = f"RD /s /q \\\?\\\"{inst_file_path_new}\""
                                            (status, uploadRes) = subprocess.getstatusoutput(cmd)
                                            if status == 0:  # 返回值代表执行成功
                                                # print(uploadRes)
                                                print(f"用批处理指令RD 删除文件{inst_file_path_new}")
                                                self.textbox_dcd.insert(END,f"[{self.get_time()}] 用批处理指令RD 删除文件{inst_file_path_new}\n")
                                                self.textbox_dcd.see(END)
                                                time.sleep(2)
                                            else:
                                                # self.progressbar_dcd.config(bootstyle="danger-striped")
                                                self.textbox_dcd.insert(END,
                                                                            f"[{self.get_time()}] fail\n")
                                                print(f"用批处理指令RD 删除文件{inst_file_path_new}")
                                                self.textbox_dcd.insert(END, f"[{self.get_time()}]执行的指令是{cmd}\n")
                                                print(uploadRes)
                                                self.textbox_dcd.insert(END,f"[{self.get_time()}] {uploadRes}\n")
                                                self.textbox_dcd.see(END)
                                                self.progressbar_dcd.config(bootstyle="danger-striped")
                                                self.progressbar_dcd["value"] = 10
                                                self.progressbar_dcd_text_value.set(value="100%")
                                                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                                sys.exit(0)
                                        else:
                                            print(f"{inst_file_path_new}文件不存在 可能已经被删除了")
                                            self.textbox_dcd.insert(END, f"[{self.get_time()}] {inst_file_path_new}文件不存在 可能已经被删除了\n")
                                            self.textbox_dcd.see(END)
                                            print(f"开始执行下一步骤文件的复制")
                                            self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] {inst_file_path_new}开始执行下一步骤文件的复制\n")
                                            self.textbox_dcd.see(END)

                                        try:
                                            os.makedirs(inst_file_path_new)
                                        except:
                                            print(f"{inst_file_path_new}文件创建fail")
                                            Messagebox.show_error(f"{inst_file_path_new}文件创建fail",
                                                                      title="Error")
                                            self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] {inst_file_path_new}文件创建fail\n")
                                            self.textbox_dcd.see(END)
                                            self.progressbar_dcd.config(bootstyle="danger-striped")
                                            self.progressbar_dcd["value"] = 10
                                            self.progressbar_dcd_text_value.set(value="100%")
                                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                            sys.exit(0)
                                        else:
                                            print(f"{inst_file_path_new}文件创建PASS，开始复制文件")
                                            self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] {inst_file_path_new}文件创建PASS，开始复制文件\n")
                                            self.textbox_dcd.see(END)
                                                # f"{inst_file_path_new}文件创建fail"

                                    # FilePath = f"{source_file}\\{v1['FilePath']}"
                                FilePath = v1['FilePath']
                                if os.path.exists(FilePath):
                                    print("文件存在，开始去复制到新的路径中去")
                                    cmd = f'Robocopy "{FilePath}" "{inst_file_path_new}" /E /R:2'
                                        # print("文件复制完成开始比较文件的MD5值")
                                        # resuit = self.compart_file_md5(inst_file_path_new, FilePath)
                                        # if not resuit:
                                        #     print("文件复制FAIL MD5 check FAIL ")
                                        #     print(cmd)
                                        #     sys.exit(0)
                                        # else:
                                        #     print("文件复制PASS MD5 check PASS ")
                                    time.sleep(1)
                                        # print(cmd)
                                    (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                                    if status == 1:  # 返回值代表执行成功
                                        print("文件复制完成开始比较文件的MD5值")
                                        self.textbox_dcd.insert(END,f"[{self.get_time()}] 文件复制完成开始比较文件的MD5值\n")
                                        self.textbox_dcd.see(END)
                                        resuit = self.compart_file_md5(inst_file_path_new, FilePath)
                                        if not resuit:
                                            print("文件复制FAIL MD5 check FAIL ")
                                            # self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件复制完成开始比较文件的MD5值\n")
                                            Messagebox.show_error("文件复制FAIL MD5 check FAIL", title="Error")
                                            print(cmd)
                                            self.progressbar_dcd.config(bootstyle="danger-stripe")
                                            self.progressbar_dcd["value"] = 10
                                            self.progressbar_dcd_text_value.set(value="100%")
                                            self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] 文件复制FAIL MD5 check FAIL\n")
                                            self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] 执行的指令是{cmd}\n")
                                            self.textbox_dcd.see(END)
                                            sys.exit(0)
                                        else:
                                            print("文件复制PASS MD5 check PASS ")
                                            self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件复制PASS MD5 check PASS\n")
                                            self.textbox_dcd.see(END)
                                            # print(uploadRes)
                                    else:
                                        print(uploadRes)
                                        Messagebox.show_error("执行程式异常终止", title="Error")
                                        print("执行程式异常终止")
                                        print(status)
                                        print(f"{cmd}")
                                        self.progressbar_dcd.config(bootstyle="danger-stripe")
                                        self.progressbar_dcd["value"] = 10
                                        self.progressbar_dcd_text_value.set(value="100%")
                                        self.textbox_dcd.insert(END,f"[{self.get_time()}] 执行的指令是{cmd}\n")
                                        self.textbox_dcd.insert(END,
                                                                    f"[{self.get_time()}] 执行的指令结果{status}\n")
                                        self.textbox_dcd.see(END)
                                        sys.exit(0)
                                else:
                                    print(f"该文件不存在{FilePath}")
                                    print("需要检擦 后期将记录在LOG文件中去")
                                    self.textbox_dcd.insert(END,f"[{self.get_time()}] 该文件不存在{FilePath}\n")
                                    self.textbox_dcd.see(END)
                                    self.progressbar_dcd.config(bootstyle="danger-stripe")
                                    self.progressbar_dcd["value"] = 10
                                    self.progressbar_dcd_text_value.set(value="100%")
                                    sys.exit(0)

                            elif kk2 == "FilePath":

                                new_file_path_name = v1['FilePath'] + "\n"
                                if new_file_path_name:
                                    self.inst_info[k2]["FilePath"] = new_file_path_name

                            else:
                                if self.inst_info[k2][kk2].find(version) != -1:
                                    self.inst_info[k2][kk2] = vv2.replace(version, v1["version"])





                            if date_time != "NA":
                                if vv2.find(f"{date_time}") != -1:
                                    self.inst_info[k2][kk2] = vv2.replace(date_time, v1["Date"])
                                    # print(f"{kk2}日期已经修改{date_time}==>{v1['Date']}")
                            else:
                                continue

        if self.inst_info and File_List:
            self.progressbar_dcd["value"] = 6
            self.progressbar_dcd_text_value.set(value="60%")
            # "inst1.ini", "FileList1.txt"
            inst_file, filelist_file = self.build_to_inst_file(self.inst_info, File_List)
            # 文件的的复制
            if os.path.exists(f"{inst_file}") and os.path.exists(f"{filelist_file}"):
                try:
                    copyfile(f"{Driver_path}\\FileList1.txt", f"{mount_file_name}\FileList.txt")
                except:
                    print(f"文件复制fail {Driver_path}\\FileList1.txt to {mount_file_name}\FileList.txt")
                    self.progressbar_dcd.config(bootstyle="danger-stripe")
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.textbox_dcd.insert(END,
                                            f"[{self.get_time()}] 文件复制fail {Driver_path}\\FileList1.txt to {mount_file_name}\FileList.txt\n")
                    self.textbox_dcd.see(END)
                    sys.exit(0)
                else:
                    try:
                        copyfile(f"{Driver_path}\\inst1.ini", f"{mount_file_name}\\I386\\inst.ini")
                    except:
                        print(f"文件复制fail {Driver_path}\inst1.ini to {mount_file_name}\\I386\\inst.ini")
                        self.progressbar_dcd.config(bootstyle="danger-stripe")
                        self.progressbar_dcd["value"] = 10
                        self.progressbar_dcd_text_value.set(value="100%")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件复制fail {Driver_path}\inst1.ini to {mount_file_name}\\I386\\inst.ini\n")
                        self.textbox_dcd.see(END)
                        sys.exit(0)
            else:
                print(f'文件不存在{inst_file}，{filelist_file}')
                self.progressbar_dcd.config(bootstyle="danger-stripe")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 文件不存在{inst_file}，{filelist_file}\n")
                self.textbox_dcd.see(END)
                sys.exit(0)
                # 修改ASUS_SWP_UX3404VA.Ver VER文件
            self.progressbar_dcd["value"] = 7
            windows_path = f"{mount_file_name}\\Windows"
            c = os.listdir(windows_path)
            ck = "(.*\.Ver$)"
            for i in c:
                if re.findall(ck, i):
                    VER = re.findall(ck, i)[0]
                    read_type = self.check_file_type(f"{windows_path}\\{VER}")
                    with open(f"{windows_path}\\{VER}", "w", encoding=read_type) as file:
                        file.write(self.Driver_CD_Name)
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功修改{windows_path}\\{VER}\n")
            self.textbox_dcd.see(END)

            # 移除MD5的文件和XLS文件
            self.progressbar_dcd["value"] = 8
            self.progressbar_dcd_text_value.set(value="80%")
            MD5 = os.listdir(f"{mount_file_name}")
            ck = "(.*\.md5$)"
            ck1 = "(.*\.xls$)"
            for i in MD5:
                if re.findall(ck, i):
                    MD5_name = re.findall(ck, i)[0]
                    os.remove(f"{mount_file_name}\\{MD5_name}")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功移除{mount_file_name}\\{MD5_name}\n")
                    self.textbox_dcd.see(END)
                elif re.findall(ck1, i):
                    xls_name = re.findall(ck1, i)[0]
                    os.remove(f"{mount_file_name}\\{xls_name}")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功移除{mount_file_name}\\{xls_name}\n")
                    self.textbox_dcd.see(END)

                # 移动xls 文件
            MD51 = os.listdir(f"{Driver_path}")
            ck1 = "(.*\.xls$)"
            for i in MD51:
                if re.findall(ck1, i):
                    xls_name = re.findall(ck1, i)[0]
                    copyfile(xls_name, f"{mount_file_name}\\{xls_name}")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功复制{mount_file_name}\\{xls_name}\n")
                    self.textbox_dcd.see(END)
            # 创建MD5值
            # os.chdir(DCD)
            # print(os.getcwd())
            if os.path.exists("fmd5x64.exe"):
                if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                    os.remove(f"{self.Driver_CD_Name}.md5")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 已经成功移除{self.Driver_CD_Name}.md5\n")
                    self.textbox_dcd.see(END)
                else:
                    cmd = f"fmd5x64.exe -r -dmount>{self.Driver_CD_Name}.md5"
                    (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                    if status == 0:  # 返回值代表执行成功
                        if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                            md5_file = []
                            read_type = self.check_file_type(f"{self.Driver_CD_Name}.md5")
                            if read_type:
                                with open(f"{self.Driver_CD_Name}.md5", "r", encoding=f"{read_type}") as files:
                                    while True:
                                        line = files.readline()
                                        md5_file.append(line)
                                        if not line:
                                            break
                                os.remove(f"{self.Driver_CD_Name}.md5")
                                md5_file = md5_file[2:]
                                with open(f"{mount_file_name}\\{self.Driver_CD_Name}.md5", "w",
                                            encoding=f"{read_type}") as files:
                                    for line in md5_file:
                                        files.write(line)
                                if os.path.exists(f"{mount_file_name}\\{self.Driver_CD_Name}.md5"):
                                    print(f"文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5")
                                    self.textbox_dcd.insert(END,
                                                                f"[{self.get_time()}] 文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5\n")
                                    self.textbox_dcd.see(END)
                    else:
                        self.textbox_dcd.insert(END,
                                                f"[{self.get_time()}] 执行程式{cmd}fail\n")
                        self.textbox_dcd.see(END)
                        self.progressbar_dcd.config(bootstyle="danger-striped")
                        self.progressbar_dcd["value"] = 10
                        self.progressbar_dcd_text_value.set(value="100%")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                        sys.exit(0)
            else:

                # C:\Users\Ben\Desktop\build_dcd
                # py_file = sys.argv[0]
                # os.path.dirname(py_file)
                tool_path = str(self.py_path) + "\\" + "fmd5x64.exe"
                # print("1111111111111111111")
                # print(Driver_path)
                # print(f"{Driver_path}/")
                # print("1111111111111111111")
                if os.path.exists(tool_path):
                    copyfile(tool_path,f"{Driver_path}\\fmd5x64.exe")
                    if os.path.exists(f"{Driver_path}\\fmd5x64.exe"):
                        if os.path.exists("fmd5x64.exe"):
                            if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                                os.remove(f"{self.Driver_CD_Name}.md5")
                                self.textbox_dcd.insert(END,
                                                        f"[{self.get_time()}] 已经成功移除{self.Driver_CD_Name}.md5\n")
                                self.textbox_dcd.see(END)
                            else:
                                cmd = f"fmd5x64.exe -r -dmount>{self.Driver_CD_Name}.md5"
                                (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                                if status == 0:  # 返回值代表执行成功
                                    if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                                        md5_file = []
                                        read_type = self.check_file_type(f"{self.Driver_CD_Name}.md5")
                                        if read_type:
                                            with open(f"{self.Driver_CD_Name}.md5", "r",
                                                      encoding=f"{read_type}") as files:
                                                while True:
                                                    line = files.readline()
                                                    md5_file.append(line)
                                                    if not line:
                                                        break
                                            os.remove(f"{self.Driver_CD_Name}.md5")
                                            md5_file = md5_file[2:]
                                            with open(f"{mount_file_name}\\{self.Driver_CD_Name}.md5", "w",
                                                      encoding=f"{read_type}") as files:
                                                for line in md5_file:
                                                    files.write(line)
                                            if os.path.exists(f"{mount_file_name}\\{self.Driver_CD_Name}.md5"):
                                                print(f"文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5")
                                                self.textbox_dcd.insert(END,
                                                                        f"[{self.get_time()}] 文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5\n")
                                                self.textbox_dcd.see(END)
                                else:
                                    self.textbox_dcd.insert(END,
                                                            f"[{self.get_time()}] 执行程式{cmd}fail\n")
                                    self.textbox_dcd.see(END)
                                    self.progressbar_dcd.config(bootstyle="danger-striped")
                                    self.progressbar_dcd["value"] = 10
                                    self.progressbar_dcd_text_value.set(value="100%")
                                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                                    sys.exit(0)
                    else:
                        print("fmd5x64.exe 工具不存在")
                        self.progressbar_dcd.config(bootstyle="danger-striped")
                        self.progressbar_dcd["value"] = 10
                        self.progressbar_dcd_text_value.set(value="100%")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有再这个路径发现{Driver_path}\\fmd5x64.exe\n")
                        self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                        self.textbox_dcd.see(END)
                        # Messagebox.show_error("没有再这个路径发现{Driver_path}\\fmd5x64.exe",
                        #                       title="fmd5x64.exe 工具不存在")
                        # sys.exit(0)
                else:
                    print("fmd5x64.exe 工具不存在")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 没有发现{tool_path}这个工具\n")
                    self.textbox_dcd.see(END)
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                    # Messagebox.show_error("没有再这个路径发现{Driver_path}\\fmd5x64.exe",
                    #                       title="fmd5x64.exe 工具不存在")
                    # sys.exit(0)
                    # # C:\Users\Ben\Desktop\build_dcd
                    # # py_file = sys.argv[0]
                    # # print(str(os.path.dirname(py_file)))
                    # tool_path = str(self.py_path) + "\\" + "fmd5x64.exe"
                    # print(Driver_path)
                    # print(f"{Driver_path}\\")
                    # if os.path.exists(tool_path):
                    #     copyfile(tool_path,f"{Driver_path}\\")
                    #     if os.path.exists(f"{Driver_path}\\fmd5x64.exe"):
                    #         if os.path.exists("fmd5x64.exe"):
                    #             if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                    #                 os.remove(f"{self.Driver_CD_Name}.md5")
                    #                 self.textbox_dcd.insert(END,
                    #                                         f"[{self.get_time()}] 已经成功移除{self.Driver_CD_Name}.md5\n")
                    #                 self.textbox_dcd.see(END)
                    #             else:
                    #                 cmd = f"fmd5x64.exe -r -dmount>{self.Driver_CD_Name}.md5"
                    #                 (status, uploadRes) = subprocess.getstatusoutput(cmd)  # 执行程式
                    #                 if status == 0:  # 返回值代表执行成功
                    #                     if os.path.exists(f"{self.Driver_CD_Name}.md5"):
                    #                         md5_file = []
                    #                         read_type = self.check_file_type(f"{self.Driver_CD_Name}.md5")
                    #                         if read_type:
                    #                             with open(f"{self.Driver_CD_Name}.md5", "r",
                    #                                       encoding=f"{read_type}") as files:
                    #                                 while True:
                    #                                     line = files.readline()
                    #                                     md5_file.append(line)
                    #                                     if not line:
                    #                                         break
                    #                             os.remove(f"{self.Driver_CD_Name}.md5")
                    #                             md5_file = md5_file[2:]
                    #                             with open(f"{mount_file_name}\\{self.Driver_CD_Name}.md5", "w",
                    #                                       encoding=f"{read_type}") as files:
                    #                                 for line in md5_file:
                    #                                     files.write(line)
                    #                             if os.path.exists(f"{mount_file_name}\\{self.Driver_CD_Name}.md5"):
                    #                                 print(f"文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5")
                    #                                 self.textbox_dcd.insert(END,
                    #                                                         f"[{self.get_time()}] 文件存在：{mount_file_name}\\{self.Driver_CD_Name}.md5\n")
                    #                                 self.textbox_dcd.see(END)


            canshu = "commit"
            self.unmount_file(mount_file_name, canshu)
            # time.sleep(1)
            # os.remove("mount")

            # CHECK MD5 值
            filename = f"{Driver_path}\\Driver64.wim"
            self.progressbar_dcd["value"] = 9
            self.progressbar_dcd_text_value.set(value="90%")
            def checkmd5(filename):

                if os.path.exists(filename):
                    md5_hash = hashlib.md5()
                    with open(filename, "rb") as f:
                        # Read and update hash in chunks of 4K
                        for byte_block in iter(lambda: f.read(4096), b""):
                            md5_hash.update(byte_block)
                        return md5_hash.hexdigest()
                else:
                    print("文件路径有问题")
                    self.textbox_dcd.insert(END,
                                                f"[{self.get_time()}] 文件路径有问题{filename}\n")
                    self.textbox_dcd.see(END)
                    self.progressbar_dcd.config(bootstyle="danger-striped")
                    self.progressbar_dcd["value"] = 10
                    self.progressbar_dcd_text_value.set(value="100%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
                        # sys.exit(0)
                    return False
                    # sys.exit(22)
                    # print(md5_hash.hexdigest())

            print("开始检查MD5值")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 开始检查MD5值\n")

            self.textbox_dcd.see(END)
            if checkmd5(filename):
                md5_num = checkmd5(filename).upper()
                file_MD5 = f"{Driver_path}\\Driver64.md5"
                read_type = self.check_file_type(f"{file_MD5}")
                with open(file_MD5, "w", encoding=read_type) as fd:
                    fd.write(md5_num)
                print("DCD Build PASS")
                tkinter.messagebox.showinfo(title="DCD Build PASS",message=f"{self.Driver_CD_Name} Build PASS")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] Driver CD:{self.Driver_CD_Name} Build PASS\n")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.see(END)
                # Messagebox.show_info("DCD Build PASS",title="PASS")
            else:
                print("MD5 FAIL")
                Messagebox.show_error("MD5 FAIL", title="Error")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] MD5 FAIL\n")
                self.textbox_dcd.see(END)

        else:
            print(f'文件不存在{inst_file}，{File_List}')
            Messagebox.show_error(f'文件不存在{inst_file}，{File_List}', title="Error")
            sys.exit(0)

    def build_drivercd(self, path_xml, Driver_path):
        os.chdir(Driver_path)
        # inst_file = r"inst.ini"
        # FileList = r"FileList.txt"
        xml_file = path_xml
        # 这里要分成几个支路
        # 如果仅仅是为了更换inst.ini file_list 等文件
        # =========================================================================
        if os.path.exists(xml_file):
            domTree = parse(f"{xml_file}")
            rootNode = domTree.documentElement
            customers = rootNode.getElementsByTagName("Part")
            resuilt = []
            self.Driver_CD_Name = ""
            for customer in customers:
                if customer.hasAttribute("Describ"):
                    Stage = customer.getAttribute("Describ")
                    resuilt.append(Stage)
                if customer.hasAttribute("modid"):
                    self.Driver_CD_Name = customer.getAttribute("modid")
            if len(resuilt) != 0:
                if "Update" in resuilt:
                    self.progressbar_dcd["value"] = 3
                    self.progressbar_dcd_text_value.set(value="30%")
                    self.textbox_dcd.insert(END, f"[{self.get_time()}] [self.copy_file] 执行程式\n")
                    self.textbox_dcd.see(END)
                    self.copy_file(Driver_path,xml_file)
                else:
                    self.progressbar_dcd["value"] = 3
                    # BUILD DCD 主程式
                    getxmlinfo, Driver_CD_Name = self.readXML(xml_file)
                    # print(getxmlinfo, Driver_CD_Name)
                    self.textbox_dcd.insert(END, f"[{self.get_time()}][self.main_build 执行程式\n")
                    self.textbox_dcd.see(END)
                    # self.copy_file(Driver_path, xml_file)
                    self.main_build(Driver_path, xml_file)


            else:
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] XML FILE 里面的内容为空\n")
                self.textbox_dcd.see(END)
                sys.exit(0)
        else:

            self.progressbar_dcd.config(bootstyle="danger-striped")
            self.progressbar_dcd["value"] = 10
            self.progressbar_dcd_text_value.set(value="100%")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] XML FILE :{xml_file} 不存在\n")
            self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~")
            self.textbox_dcd.see(END)
            sys.exit(0)

    def on_browse7(self):
        # 获取dcd file和 XML的编译文件
        # self.path_ent_xml
        # self.path_var_DCD
        def start():
            self.progressbar_dcd.config(bootstyle="Success-striped")
            path_xml = self.path_ent_xml.get().strip(" ").strip("\n")
            Driver_path = self.path_ent_dcd.get().strip(" ").strip("\n")
            self.progressbar_dcd["value"] = 1
            self.progressbar_dcd_text_value.set(value="10%")
            if Driver_path and path_xml:
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 选择的Driver CD文件是{Driver_path}\n")
                self.textbox_dcd.see(END)
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 选择的编译的XML文件是{path_xml}\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd["value"] = 2
                self.progressbar_dcd_text_value.set(value="20%")
                self.build_drivercd(path_xml, Driver_path)
            else:
                # Messagebox.show_error("没有定义Driver_path&path_xml两个文件")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] FAIL: 没有选择Driver CD file&XML file\n")
                self.textbox_dcd.see(END)
                self.progressbar_dcd.config(bootstyle="danger-striped")
                self.progressbar_dcd["value"] = 10
                self.progressbar_dcd_text_value.set(value="100%")
                self.textbox_dcd.insert(END, f"[{self.get_time()}] 程式终止/(ㄒoㄒ)/~~\n")
                # time.sleep(1)
                # Messagebox.show_error("没有定义Driver_path&path_xml两个文件", title="Error")


        self.t1 = Thread(target=start)
        self.t1.setDaemon(True)
        self.t1.start()

if __name__ == '__main__':
    def main():
        app = ttk.Window("Beitou_DCD_Build_Tool_v2.4", "darkly")
        Buildxmlfile(app)
        app.mainloop()

    firt = Thread(target=main())
    # firt.setDaemon(True)
    firt.start()
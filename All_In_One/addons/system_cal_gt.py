bl_info = {
    "name": "Tinh Toan Neo",
    "author": "Cong Ty TNHH 1 MTV G6T",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "View3D > NEO",
    "description": "Nguyen Ly Gia Co - NEO",
    "warning": "",
    "wiki_url": "",
    "category": "NEO"
    }

import bpy
from bpy.props import *
from bpy.app.handlers import persistent
import math
from mpmath import *
from mathutils import Vector  # 3d cursor
import numpy as np
import matplotlib.pyplot as plt
import bmesh
import sympy as sp
#from sympy.plotting import plot
from sympy import *

op = bpy.ops
me = op.mesh

import urllib.request
from urllib.error import URLError, HTTPError
pm_neo_url = 'http://tdkt5.g6t.vn/ws_pm_neo.php?key=123456'

## Check Active
try:
	data = urllib.request.urlopen(pm_neo_url).read()
	#type(data)
	print(data)
	if data.decode("utf-8") == '1':
		print("Phan mem dang active")
	else:
		print("Phan em khong duoc active")
		exit()
except HTTPError as e:
	# do something
	print('Error code: ', e.code)
	exit()
except URLError as e:
	# do something (set req to blank)
	print('Reason: ', e.reason)
	exit()
## END Check Active	

# Set Default Value
arrChonLoai = [('1', 'Modul đàn hồi', ''),  # VD:('hinh_tron', 'Hình Tròn', 1)
               ('2', 'Ứng suất pháp tuyến', ''),
			   ('3', 'Ứng suất tiếp tuyến', ''),
			   ('4', 'Chuyển vị', ''),
			   ('5', 'Biến dạng', '')]
arrDieuKienLoKhoan = [('KHO', 'Khô', ''), ('AM', 'Ẩm', '')]
arrLoaiDatDa = [('RAN', 'Rắn', ''), ('YEU', 'Yếu', '')]
arrThepNhom = [('A1', 'A-I', ''), ('A2', 'A-II', ''), ('A3', 'A-III', '')]

# arrNguyenLy = ['Default', '1.Nguyên lý Treo', '2.Nguyên lý Bản dầm', '3.Nguyên lý Gia cố', '4.Nguyên lý Nêm', '5.Nguyên lý tương tác']

# Lấy ra Scene Name của màn hình hiện tại (Các Nguyên lý) : Có  thể dùng chung biến nguyenLy
#
#    Tab Panel NEO
#
class ToolPanel_NEO(bpy.types.Panel):
	bl_label 			= "Dữ liệu đầu vào của NEO"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "NEO"

	def draw(self, context):
		layout 			= self.layout
		scn 			= context.scene

		box 			= layout.box()
		col 			= box.column()
		title_size 		= 0.8

		# screen window
		# if bpy.context.screen.scene.name == 'Scripting.001':

		# lấy ra tên màn hình Nguyên lý
		nguyenLy 		= bpy.context.screen.scene.name

		# Scene
		if nguyenLy[0] == '1':
			# todo
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DuongKinhThepNeo_Dn_NL1')
			row.label("(m)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ThepNhom_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhaNangChiuKeoThepNeo_Rk_NL1')
			row.label("(MPa)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DuongKinhLoKhoan_Dlk_NL1')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'LucDinhKetGiuaBeTongVaThanhNeo_T1_NL1')
			row.label("(MPa)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'LucDinhKetGiuaBeTongVaDatDa_T2_NL1')
			row.label("(MPa)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DieuKienLoKhoan_Dlv_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoLamViecCuaKhoaNeo_Dlvz_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoLamViecCuaNeo_Dlv_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoTapTrungUngSuatKeo_K2_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoTapTrungUngSuat_K1_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDaiNeoNhoRaMatLo_Lk_NL1')
			row.label("(m)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoQuaTaiNocLo_Np_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoQuaTaiHongLo_Nph_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoDieuChinhChieuDaiKhoaNeo_Kz_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDaiKhoaNeo_Lz_NL1')
			row.label("(m)")

			bpy.app.handlers.scene_update_post.append(cb_scene_update)
			EventWatcher.AddWatcher(
				EventWatcher(bpy.data.scenes[nguyenLy], "ThepNhom_NL1", CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "DieuKienLoKhoan_Dlv_NL1", CompareLocation,
												 CompareLocationCallback, True))

		elif nguyenLy[0] == '2':
			# todo
			print("Neo: NguyenLy2")
			# Khoảng cách giữa các Neo
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhoangCachGiuaCacNeo_S_NL2')
			row.label("(m)")

			# Hệ số phụ thuộc vào thời gian lắp đặt Neo
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoPhuThuocThoiGianLapDatNeo_NL2')
			row.label(" ")

			# Diện tích vùng gia tải của 1 thanh neo
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DienTichVungGiaTai1ThanhNeo_A_NL2')
			row.label("(m2)")

			# Chiều dài của Neo
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDaiCuaNeo_L_NL2')
			row.label("(m)")

			# Bán Kinh chịu cắt của Đơn vị đất đá được gia cố
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'BankinhChiuCatCuaDVDatDaDuocGiaCo_NL2')
			row.label("(m)")

		elif nguyenLy[0] == '3':
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DuongKinhThepNeoDb_NL3')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoiThepNeoEb_NL3')
			row.label("(Mpa)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoiVuaXiMangEg_NL3')
			row.label("(Mpa)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DuongKinhLoKhoanDh_NL3')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDaiNeoL_NL3')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhoangCachNeoA_NL3')
			row.label("(m)")

		elif nguyenLy[0] == '4':
			# todo
			print("Neo: NguyenLy4")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhaNangChiuLuc1ThanhNeo_NL4')
			row.label("(T)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDai1ThanhNeo_NL4')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'SoLuongNeoGiuKhoiNem_NL4')
			row.label(" ")

		elif nguyenLy[0] == '5':
			# todo
			print("Neo: NguyenLy5")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DuongKinhThepNeoDb_NL5')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DuongKinhLoKhoanDh_NL5')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoiThepNeoEb_NL5')
			row.label("(GPa)")

			'''row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoiVuaNeo_Eg_NL5')
			row.label("(MPa)")'''

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoiTruotVuaNeo_Gg_NL5')
			row.label("(MPa)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDaiNeoL_NL5')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhoangCachNeoA_NL5')
			row.label("(m)")

			'''row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoPoissonNeo_NL5')
			row.label(" ")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoPoissonVuaNeo_NL5')
			row.label(" ")'''
		else:
			# todo
			print('Neo: Default')


#
#    Tab Panel Dat Da
#
class ToolPanel_DATDA(bpy.types.Panel):
	bl_label 			= "Dữ liệu đầu vào của Đất Đá"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "Đất Đá"

	def draw(self, context):
		layout 			= self.layout
		scn 			= context.scene
		# layout.prop(scn, 'MyCustomInt', icon='BLENDER', toggle=True)
		# layout.prop(scn, 'ChonLoai')
		box 			= layout.box()
		col 			= box.column()
		title_size 		= 0.8

		# lấy ra tên màn hình Nguyên lý
		nguyenLy = bpy.context.screen.scene.name

		if nguyenLy[0] == '1':  # Nguyên lý 1
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoKienCoTBDatDa_f_NL1')
			row.label(" ")
			
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TrongLuongTheTich_NL1')
			row.label("(T/m3)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'UngSuatKeoDatDaVach_NL1')
			row.label("(MPa)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'UngSuatNenDatDaVach_NL1')
			row.label("(MPa)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocMaSatTrong_NL1')
			row.label("(độ)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HoSoPoisson_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'LoaiDatDa_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoLuuBien_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoTapTrungUngSuatKeo_K2_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoTapTrungUngSuat_K1_NL1')
			row.label(" ")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDayPhanLopTrungBinhB_NL1')
			row.label("(m)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoGiamYeuCauTrucKc_NL1')
			row.label(" ")
			
			
			bpy.app.handlers.scene_update_post.append(cb_scene_update)
			EventWatcher.AddWatcher(
				EventWatcher(bpy.data.scenes[nguyenLy], "LoaiDatDa_NL1", CompareLocation, CompareLocationCallback,
							 True))

		elif nguyenLy[0] == '2':  # Nguyên lý 2
			print("Dat Da - Nguyen ly 2")
			# Trọng lượng riêng của dầm đá mang tải
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TrongLuongRiengCuaDamDaMangTai_NL2')
			row.label("(KN/m3)")

			# Góc ma sát trong
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocMaSatTrong_NL2')
			row.label("(độ)")

			# Tỷ số giữa áp lục ngang trung bình và áp lực thằng đứng trung bình
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TySoGiuaApLucNgangVaThangDungTB_K_NL2')
			row.label(" ")

			# Lực kết dính giữa các lớp đất đá
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'LucKetDinhGiuaCacLopDatDa_c_NL2')
			row.label("(MPA)")

			# Chiều cao vùng đất đá không gây ứng suất
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuCaoVungDatDaKhongGayUngSuat_D_NL2')
			row.label("(m)")

			# Bán kính
			'''row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'BanKinh_r_NL2')
			row.label("(m)")'''

		elif nguyenLy[0] == '3':  # Nguyên lý 3
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TrongLuongTheTich_NL3')
			row.label("(T/m3)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoiDaEr_NL3')
			row.label("(Mpa)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoPoisson_NL3')
			row.label(" ")

		elif nguyenLy[0] == '4':  # Nguyên lý 4
			#  Trọng lượng thể tích đất đá
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TrongLuongTheTichDatDa_NL4')
			row.label("(T/m3)")

			box = layout.box()
			col = box.column()
			
			#  Góc dốc
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocDoc_1_NL4')
			row.label("(độ)")

			#  Góc phương vị của khe nứt
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocPhuongVi_1_NL4')
			row.label("(độ)")

			#  Tên khe nứt
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TenKheNut_1_NL4')
			row.label(" ")
			
			# Tao khoang cach giua cac dong
			col.separator()

			#  Góc dốc
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocDoc_2_NL4')
			row.label("(độ)")

			#  Góc phương vị của khe nứt
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocPhuongVi_2_NL4')
			row.label("(độ)")

			#  Tên khe nứt
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TenKheNut_2_NL4')
			row.label(" ")

			# Tao khoang cach giua cac dong
			col.separator()
			
			#  Góc dốc
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocDoc_3_NL4')
			row.label("(độ)")

			#  Góc phương vị của khe nứt
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocPhuongVi_3_NL4')
			row.label("(độ)")

			#  Tên khe nứt
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TenKheNut_3_NL4')
			row.label(" ")

			
			box = layout.box()
			col = box.column()
			# Thể tích khối NÊM nóc
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TheTich_KhoiNem_Noc_NL4')
			row.label("(m3)")

			# Trọng lượng khối NÊM nóc
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'TrongLuong_KhoiNem_Noc_NL4')
			row.label("(T)")

			# Hệ số an toàn khối NÊM nóc
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSo_AnToan_KhoiNem_Noc_NL4')
			row.label(" ")

			row = layout.row()
			layout.operator("ui_custom.nguyenly4", icon='PLUGIN')

		elif nguyenLy[0] == '5':  # Nguyên lý 5
			# Độ bền nén đơn trục
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'DoBenNenDonTruc_NL5')
			row.label("(MPa)")

			# Modul đàn hồi Er
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoi_Em_NL5')
			row.label("(GPa)")

			# Modul đàn hồi trượt Gm
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ModulDanHoiTruot_Gm_NL5')
			row.label("(GPa)")

			# Hệ số Poisson
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoPoisson_NL5')
			row.label(" ")

			# Áp lực nước ngầm Po
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ApLucNuocNgamPo_NL5')
			row.label("(MPa)")


#
#    Tab Panel Cong Trinh Ngam
#
class ToolPanel_CongTrinhNgam(bpy.types.Panel):
	bl_label 			= "Dữ liệu đầu vào của Công Trình Ngầm"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "Công Trình Ngầm"

	def draw(self, context):
		layout 			= self.layout
		scn 			= context.scene

		box 			= layout.box()
		col 			= box.column()
		title_size 		= 0.8

		# lấy ra tên màn hình Nguyên lý
		nguyenLy = bpy.context.screen.scene.name

		if nguyenLy[0] == '1':  # Nguyên lý 1			
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuSauH_NL1')
			row.label("(m)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuRong2a_NL1')
			row.label("(m)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuCaoH1_NL1')
			row.label("(m)")

			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuCaoTuongLoH2_NL1')
			row.label("(m)")
			
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDai_NL1')
			row.label("(m)")

		elif nguyenLy[0] == '2':  # Nguyên lý 2
			print("Cong Trinh Ngam - Nguyen Ly 2")
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuRongCongTrinh_NL2')
			row.label("(m)")
			
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuCaoCongTrinh_NL2')
			row.label("(m)")

		elif nguyenLy[0] == '3':			
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuSauCTN_NL3')
			row.label("(m)")

			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'BanKinhCTN_NL3')
			row.label("(m)")

		elif nguyenLy[0] == '4':			
			#  Góc dốc của Công trình ngầm
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocDoc_CongTrinhNgam_NL4')
			row.label("(độ)")

			#  Góc phương vị của Công trình ngầm
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'GocPhuongVi_CongTrinhNgam_NL4')
			row.label("(độ)")

			#  Chiều rộng của Công trình ngầm
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuRong_CongTrinhNgam_NL4')
			row.label("(m)")

		elif nguyenLy[0] == '5':
			#  Bán kính Ra
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'BanKinhRa_NL5')
			row.label("(m)")


#
#	Tab Panel Đầu ra: Hiển thị kết quả đầu ra, Vẽ đồ thị, tính toán, mô phỏng
#
class initOutPut(bpy.types.Panel):
	bl_label 			= "Dữ liệu đầu ra"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"  # TOOL_PROPS
	bl_idname 			= "ui.output"
	bl_category 		= "Kết quả"
	resultCV 			= bpy.props.StringProperty()

	def draw(self, context):
		ob 			= context.object
		layout 		= self.layout
		scn 		= context.scene

		title_size 	= 0.8

		# lấy ra tên màn hình Nguyên lý
		nguyenLy 	= bpy.context.screen.scene.name

		if nguyenLy[0] == '1':
			row = layout.row()
			row.operator("ui_custom.nguyenly1", icon='PLUGIN')
			row.operator("ui_custom.nguyenly1_dothi", icon='FCURVE')
			row.operator("ui_custom.nguyenly1_cap_nhat_dothi", icon='FILE_REFRESH')
			# tạo khoảng cách giữa dòng
			layout.separator()
			
			# New box
			box = layout.box()
			col = box.column()

			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoOnDinhDatDaVach_Nv_NL1')
			row.label(" ")
						
			row = col.split(percentage=100, align=True)
			row.prop(scn, 'ThongBaoNv')
			
			#row.label(text="Thông báo Nv")
			# row = layout.row()
			# row.label(text="Hello world!", icon='WORLD_DATA')
			# row = layout.row()
			
			# New box
			box = layout.box()
			col = box.column()
			
			row = col.split(percentage=title_size, align=True)
			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row.prop(scn, 'HeSoOnDinhDatDaHong_Nh_NL1')
			row.label(" ")
			
			row = col.split(percentage=100, align=True)
			row.prop(scn, 'ThongBaoNh')
			
			# New box
			box = layout.box()
			col = box.column()
			
			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuCaoVomSupLo_B_NL1')
			row.label("(m)")
			
			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhaNangChiuLuc1ThanhNeo_Pn_NL1')
			row.label("(MN)")

			# New box
			box = layout.box()
			col = box.column()

			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDai1ThanhNeoNoc_Ln_NL1')
			row.label("(m)")

			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'MatDoNeoVach_Sn_NL1')
			row.label("(neo/m2)")

			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhoangCachNeoVach_A1_NL1')
			row.label("(m)")
			
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhoangCachNeoVachTheoChuVi_NL1')
			row.label("(m)")
			
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhoangCachNeoVachTheoTruc_NL1')
			row.label("(m)")
			
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'SoLuongNeoVach_NL1')
			row.label("(thanh)")
			
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoAnToanNocLo_Np_NL1')
			row.label(" ")
			
			# New box
			box = layout.box()
			col = box.column()

			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'ChieuDai1ThanhNeoHong_Lh_NL1')
			row.label("(m)")

			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'MatDoNeoHong_Sh_NL1')
			row.label("(neo/m2)")

			row = layout.row()
			# row.label(text="Hệ số ổn định đất đá vách Nv")
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'KhoangCachNeoHong_A2_NL1')
			row.label("(m)")
			
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'SoLuongNeoHong_NL1')
			row.label("(thanh)")
			
			row = layout.row()
			row = col.split(percentage=title_size, align=True)
			row.prop(scn, 'HeSoAnToanHongLo_Nph_NL1')
			row.label(" ")
			
			# Xử lý cập nhật theo từng nút: 
			bpy.app.handlers.scene_update_post.append(cb_scene_update)
		
			# Thông báo theo hệ số ổn định thay đổi
			# EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "HeSoOnDinhDatDaVach_Nv_NL1", CompareLocation, CompareLocationCallback, True))
			# EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "HeSoOnDinhDatDaHong_Nh_NL1", CompareLocation, CompareLocationCallback, True))
			
			# neo vách
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "MatDoNeoVach_Sn_NL1", CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "KhoangCachNeoVachTheoChuVi_NL1", CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "KhoangCachNeoVachTheoTruc_NL1", CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "ChieuDai1ThanhNeoNoc_Ln_NL1", CompareLocation, CompareLocationCallback, True))
			
			# neo hông
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], 'ChieuDai1ThanhNeoHong_Lh_NL1', CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], 'KhoangCachNeoHong_A2_NL1', CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], 'MatDoNeoHong_Sh_NL1', CompareLocation, CompareLocationCallback, True))

		elif nguyenLy[0] == '2':
			print("Dau ra - Nguyen ly 2")
			row = layout.row()
			row.operator("ui_custom.nguyenly2", icon='PLUGIN')
			row.operator("ui_custom.nguyenly2_dothi", icon='FCURVE')
			
			layout.separator()
			
			# Lực kéo neo đơn vị T
			box = layout.box()
			col = box.column()

			row = layout.row()
			row = col.split(percentage=0.85, align=True)
			row.prop(scn, 'LucKeoNeoDonVi_T_NL2')
			row.label("(KN)")

		elif nguyenLy[0] == '3':
			# New box
			# box = layout.box()
			# col = box.column()

			layout.prop(scn, 'ChonLoai')

			row = layout.row()
			row.operator("ui_custom.nguyenly3", icon='PLUGIN')
			row.operator("ui_custom.nguyenly3_dothi", icon='FCURVE')

			row = layout.row()
			row.prop(scn, 'OutBanKinh_NL3')
			# view = context.space_data
			# row = col.split(percentage=title_size, align=True)
			col = layout.column()
			row = layout.row()
			row.label(text="")
			row.label(text="TT sau khi Neo")
			row.label(text="TT trước khi Neo")
			row.label("ĐVT")

			row = layout.row()
			row.label(text="Ứng Suất pháp tuyến")
			row.prop(scn, 'UngSuatPhapTuyenSau_NL3')
			row.prop(scn, 'UngSuatPhapTuyenTruoc_NL3')
			row.label("(m)")

			row = layout.row()
			row.label(text="Ứng Suất tiếp tuyến")
			row.prop(scn, 'UngSuatTiepTuyenSau_NL3')
			row.prop(scn, 'UngSuatTiepTuyenTruoc_NL3')
			row.label("(m)")

			row = layout.row()
			row.label(text="Biến dạng")
			row.prop(scn, 'BienDangSau_NL3')
			row.prop(scn, 'BienDangTruoc_NL3')
			row.label("(m)")

			row = layout.row()
			row.label(text="Chuyển vị")
			row.prop(scn, 'ChuyenViSau_NL3')
			row.prop(scn, 'ChuyenViTruoc_NL3')
			row.label("(m)")

			row = layout.row()
			row.label(text="Modul đàn hồi")
			row.prop(scn, 'ModulDanHoiSau_NL3')
			row.prop(scn, 'ModulDanHoiTruoc_NL3')
			row.label("(m)")

			bpy.app.handlers.scene_update_post.append(cb_scene_update)
			EventWatcher.AddWatcher(
				EventWatcher(bpy.data.scenes[nguyenLy], "cursor_location", CompareLocation, CompareLocationCallback,
							 True))
			EventWatcher.AddWatcher(
				EventWatcher(bpy.data.scenes[nguyenLy], 'ChonLoai', CompareLocation, CompareLocationCallback, True))

		elif nguyenLy[0] == '4':
			# Thể tích khối NÊM
			'''row = layout.row()
			row.prop(scn, 'TheTich_KhoiNem_Noc_NL4')
			row.label("(m3)")'''

			row = layout.row()
			layout.operator("ui_custom.nguyenly4", icon='PLUGIN')

		elif nguyenLy[0] == '5':
			layout.operator("ui_custom.nguyenly5", icon='PLUGIN')
			
			layout.separator()
			
			# Lực kéo neo đơn vị T
			box = layout.box()
			col = box.column()

			row = layout.row()
			row = col.split(percentage=0.85, align=True)
			row.prop(scn, 'BanKinhVungDanHoi_Re_NL5')
			row.label("(m)")
			
			row = layout.row()
			row = col.split(percentage=0.85, align=True)
			row.prop(scn, 'BanKinhVungDeo_Rf_NL5')
			row.label("(m)")


#
#    KEt Qua Tinh: NEO - Dat Da - Cong Trinh Ngam
#
# scn = bpy.context.scene

## Xử lý tính toán (Vẽ Đồ thị) - Nguyên lý 1
class KetQuaTinh_NguyenLy_1(bpy.types.Operator):
	bl_idname 		= "ui_custom.nguyenly1"
	bl_label 		= "Tính Toán"
	bl_space_type 	= "VIEW_3D"
	bl_region_type 	= "TOOLS"
	bl_category 	= "NEO"

	def execute(self, context):
		print("self", self)
		#self.report({'INFO'}, "Hello world!")
		# scn 		= context.scene
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		if nguyenLy[0] == '1':
			# ToDo
			print('Dang xu ly su kien tinh toan')
			nguyenLy1 = NguyenLy1(bpy.data.scenes[nguyenLy].DuongKinhThepNeo_Dn_NL1,
								  bpy.data.scenes[nguyenLy].KhaNangChiuKeoThepNeo_Rk_NL1,
								  bpy.data.scenes[nguyenLy].DuongKinhLoKhoan_Dlk_NL1,
								  bpy.data.scenes[nguyenLy].LucDinhKetGiuaBeTongVaThanhNeo_T1_NL1,
								  bpy.data.scenes[nguyenLy].LucDinhKetGiuaBeTongVaDatDa_T2_NL1,
								  bpy.data.scenes[nguyenLy].HeSoLamViecCuaNeo_Dlv_NL1,
								  bpy.data.scenes[nguyenLy].HeSoLamViecCuaKhoaNeo_Dlvz_NL1,
								  bpy.data.scenes[nguyenLy].ChieuDaiNeoNhoRaMatLo_Lk_NL1,
								  bpy.data.scenes[nguyenLy].HeSoQuaTaiNocLo_Np_NL1,
								  bpy.data.scenes[nguyenLy].HeSoQuaTaiHongLo_Nph_NL1,
								  bpy.data.scenes[nguyenLy].HeSoDieuChinhChieuDaiKhoaNeo_Kz_NL1,
								  bpy.data.scenes[nguyenLy].ChieuDaiKhoaNeo_Lz_NL1,
								  bpy.data.scenes[nguyenLy].TrongLuongTheTich_NL1,
								  bpy.data.scenes[nguyenLy].UngSuatKeoDatDaVach_NL1,
								  bpy.data.scenes[nguyenLy].UngSuatNenDatDaVach_NL1,
								  bpy.data.scenes[nguyenLy].GocMaSatTrong_NL1,
								  bpy.data.scenes[nguyenLy].HoSoPoisson_NL1,
								  bpy.data.scenes[nguyenLy].LoaiDatDa_NL1,
								  bpy.data.scenes[nguyenLy].HeSoLuuBien_NL1,
								  bpy.data.scenes[nguyenLy].HeSoTapTrungUngSuatKeo_K2_NL1,
								  bpy.data.scenes[nguyenLy].HeSoTapTrungUngSuat_K1_NL1,
								  bpy.data.scenes[nguyenLy].ChieuDayPhanLopTrungBinhB_NL1,
								  bpy.data.scenes[nguyenLy].HeSoGiamYeuCauTrucKc_NL1,
								  bpy.data.scenes[nguyenLy].HeSoKienCoTBDatDa_f_NL1,
								  bpy.data.scenes[nguyenLy].ChieuSauH_NL1,
								  bpy.data.scenes[nguyenLy].ChieuRong2a_NL1,
								  bpy.data.scenes[nguyenLy].ChieuCaoH1_NL1,
								  bpy.data.scenes[nguyenLy].ChieuCaoTuongLoH2_NL1)

			# Đầu ra
			bpy.data.scenes[nguyenLy].HeSoOnDinhDatDaVach_Nv_NL1 = nguyenLy1.he_so_on_dinh_dat_da_vach_Nv
			bpy.data.scenes[nguyenLy].HeSoOnDinhDatDaHong_Nh_NL1 = nguyenLy1.he_so_on_dinh_dat_da_hong_Nh
			bpy.data.scenes[nguyenLy].ChieuCaoVomSupLo_B_NL1 = nguyenLy1.chieu_cao_vom_sup_lo_B
			bpy.data.scenes[nguyenLy].KhaNangChiuLuc1ThanhNeo_Pn_NL1 = nguyenLy1.kha_nang_chiu_luc_1_thanh_neo_Pn
			bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoNoc_Ln_NL1 = nguyenLy1.chieu_dai_1_thanh_neo_noc_Ln
			bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoHong_Lh_NL1 = nguyenLy1.chieu_dai_1_thanh_neo_hong_Lh
			bpy.data.scenes[nguyenLy].MatDoNeoVach_Sn_NL1 = nguyenLy1.mat_do_neo_vach_Sn
			bpy.data.scenes[nguyenLy].KhoangCachNeoVach_A1_NL1 = nguyenLy1.khoang_cach_neo_vach_A1
			bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1 = nguyenLy1.khoang_cach_neo_vach_A1
			bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1 = nguyenLy1.khoang_cach_neo_vach_A1
			bpy.data.scenes[nguyenLy].SoLuongNeoVach_NL1 = round((3.14 * bpy.data.scenes[nguyenLy].ChieuRong2a_NL1 / 2) / (nguyenLy1.khoang_cach_neo_vach_A1), 0) + 1
			bpy.data.scenes[nguyenLy].MatDoNeoHong_Sh_NL1 = nguyenLy1.mat_do_neo_hong_Sh
			bpy.data.scenes[nguyenLy].KhoangCachNeoHong_A2_NL1 = nguyenLy1.khoang_cach_neo_hong_A2
			bpy.data.scenes[nguyenLy].SoLuongNeoHong_NL1 = round((3.14 * bpy.data.scenes[nguyenLy].ChieuRong2a_NL1 / 2) / (nguyenLy1.khoang_cach_neo_hong_A2), 0) + 1
			
			Nv = nguyenLy1.he_so_on_dinh_dat_da_vach_Nv
			Nh = nguyenLy1.he_so_on_dinh_dat_da_hong_Nh
			# Nv = 4
			# Nh = 1
			lonhonbang4		= "* Có thể không cần chống lò..."
			nhohonbang1		= "**Nên chống bằng vì sắt hoặc bê tông..."
			trongkhoang14 	= "Có thể sử dụng vì kéo neo kết hợp BTP"
			
			if Nv >= 4 or Nh >= 4 :
				self.report({'WARNING'}, lonhonbang4)
			elif Nv <= 1 or Nh <= 1:
				self.report({'WARNING'}, nhohonbang1)
			
			if Nv >= 4:
				bpy.data.scenes[nguyenLy].ThongBaoNv = lonhonbang4
			elif Nv <= 1:
				bpy.data.scenes[nguyenLy].ThongBaoNv = nhohonbang1
			else:
				bpy.data.scenes[nguyenLy].ThongBaoNv = trongkhoang14
			
			if Nh >= 4:
				bpy.data.scenes[nguyenLy].ThongBaoNh = lonhonbang4
			elif Nh <= 1:
				bpy.data.scenes[nguyenLy].ThongBaoNh = nhohonbang1
			else:
				bpy.data.scenes[nguyenLy].ThongBaoNh = trongkhoang14
		return {'FINISHED'}

## Vẽ đồ thị - Nguyên lý 1
class dothi_NguyenLy_1(bpy.types.Operator):
	bl_idname 		= "ui_custom.nguyenly1_dothi"
	bl_label 		= "Mô phỏng"
	bl_space_type 	= "VIEW_3D"
	bl_region_type 	= "TOOLS"
	bl_category 	= "NEO"
	
	def execute(self, context):
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly ve do thi')
		if nguyenLy[0] == '1':
			print('Mo phong Nguyen ly 1')
			ct_2a			= bpy.data.scenes[nguyenLy].ChieuRong2a_NL1				#5
			ct_h			= bpy.data.scenes[nguyenLy].ChieuCaoH1_NL1				#4
			ct_ht			= bpy.data.scenes[nguyenLy].ChieuCaoTuongLoH2_NL1		#1
			ct_chieudai 	= bpy.data.scenes[nguyenLy].ChieuDai_NL1 					#10
			n_L 			= bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoNoc_Ln_NL1 			# 2
			n_R 			= 0.01
			n_soluong 		= bpy.data.scenes[nguyenLy].SoLuongNeoVach_NL1#7
			n_khoangcach 	= bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1		#1.2
			n_khoangcachdoc = bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1	#2
			
			# Set về object mode
			if op.object.mode_set(mode='EDIT'):
				op.object.mode_set(mode='OBJECT')
			# Lam sach man hinh
			scene = bpy.context.scene
			for ob in scene.objects:
				ob.select = True
			bpy.ops.object.delete()

			# DAY LO
			bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
			# Ve
			bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False, enter_editmode=False,
												   location=(0.0, 0.0, 0.0),
												   layers=(
												   True, False, False, False, False, False, False, False, False, False,
												   False, False, False,
												   False, False, False, False, False, False, False))
			# Doi ten doi tuong duoc chon thanh """"Đáy lò 1""""
			for obj in bpy.context.selected_objects:
				obj.name = "daylo1"
			# Thiet lap chieu rong day lo
			bpy.context.object.dimensions[0] = ct_2a

			# TUONG LO TRAI
			# Ve
			bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False, enter_editmode=False,
												   location=(-ct_2a / 2, 0.0, ct_ht / 2),
												   layers=(
												   True, False, False, False, False, False, False, False, False, False,
												   False, False, False,
												   False, False, False, False, False, False, False))
			# Doi ten doi tuong duoc chon thanh """"Tường lò trái""""
			for obj in bpy.context.selected_objects:
				obj.name = "tuonglotrai"
			# Thiet lap chieu cao tuong lo
			bpy.context.object.dimensions[0] = ct_ht
			bpy.context.object.rotation_euler[1] = 4.71239

			# TUONG LO PHAI
			# Ve
			bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False, enter_editmode=False,
												   location=(ct_2a / 2, 0.0, ct_ht / 2),
												   layers=(
												   True, False, False, False, False, False, False, False, False, False,
												   False, False, False,
												   False, False, False, False, False, False, False))
			# Doi ten doi tuong duoc chon thanh "Tường lò phải"
			for obj in bpy.context.selected_objects:
				obj.name = "tuonglophai"
			# Thiet lap chieu cao tuong lo
			bpy.context.object.dimensions[0] = ct_ht
			bpy.context.object.rotation_euler[1] = 4.71239

			# TAM DUONG LO
			# Ve
			bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False, enter_editmode=False,
												   location=(0.0, ct_chieudai / 2, 0.0),
												   layers=(
												   True, False, False, False, False, False, False, False, False, False,
												   False, False, False,
												   False, False, False, False, False, False, False))
			# Doi ten doi tuong duoc chon thanh "Tâm lò"
			for obj in bpy.context.selected_objects:
				obj.name = "tamlo"
			# Thiet lap chieu dai tam lo
			bpy.context.object.dimensions[0] = ct_chieudai
			bpy.context.object.rotation_euler[2] = 1.5708

			# Them 1 thanh neo: ban kinh, chieu dai, toa do.
			bpy.ops.mesh.primitive_cylinder_add(radius=n_R, depth=n_L, view_align=False, enter_editmode=False,
												location=(0, 0, ct_h + n_L / 2), layers=(
				True, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
				False, False, False, False, False))

			# Doi ten doi tuong duoc chon thanh "Neo1"
			for obj in bpy.context.selected_objects:
				obj.name = "neo1"
			# Dat con tro vao 1 dau Neo
			bpy.context.scene.cursor_location = (0.0, 0.0, ct_2a - n_L / 2)
			# Thiet lap goc toa do cho thanh neo
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			bpy.ops.object.modifier_add(type='ARRAY')
			# bpy.context.object.modifiers[""""""""Array""""""""].use_relative_offset = False
			# bpy.context.object.modifiers[""""""""Array""""""""].use_constant_offset = True
			# bpy.context.object.modifiers[""""""""Array""""""""].fit_type = 'FIXED_COUNT'
			# bpy.context.object.modifiers[""""""""Array""""""""].count = 6
			# bpy.context.object.modifiers[""""""""Array""""""""].constant_offset_displace[0] = 1



			# Tao duong dan cac thanh neo
			bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False, enter_editmode=False,
												   location=(0, 0, ct_h), layers=(
				True, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
				False, False, False, False, False))
			#op.object.mode_set(mode='EDIT')
			#bpy.context.active_object.data.splines[0].points[0].select = True
			#bpy.ops.transform.translate(value=(-ct_2a/2, 0.0, -(ct_h - ct_ht), 1.0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
			
			bpy.context.active_object.data.splines[0].points[0].co = (-ct_2a/2, 0.0, -(ct_h - ct_ht), 1.0)
			bpy.context.active_object.data.splines[0].points[4].co = (ct_2a/2, 0.0, -(ct_h - ct_ht), 1.0)
			# Doi ten doi tuong duoc chon thanh "noclo1"
			for obj in bpy.context.selected_objects:
				obj.name = "noclo1"

			# Bo chon duong dan noc lo
			bpy.data.objects['noclo1'].select = False
			# Chon neo
			bpy.data.objects['neo1'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['neo1']
			# Chon duong dan cua Neo
			bpy.ops.object.modifier_add(type='CURVE')
			bpy.context.object.modifiers["Curve"].object = bpy.data.objects["noclo1"]

			# bpy.ops.object.modifier_add(type='ARRAY')
			bpy.context.object.modifiers["Array"].count = n_soluong

			bpy.context.object.modifiers["Array"].use_constant_offset = True
			bpy.context.object.modifiers["Array"].constant_offset_displace[0] = n_khoangcach
			bpy.context.object.modifiers["Array"].use_relative_offset = False

			bpy.ops.object.modifier_add(type='ARRAY')
			bpy.context.object.modifiers["Array.001"].use_relative_offset = False
			bpy.context.object.modifiers["Array.001"].use_constant_offset = True
			bpy.context.object.modifiers["Array.001"].constant_offset_displace[1] = n_khoangcachdoc
			bpy.context.object.modifiers["Array.001"].count = round(ct_chieudai/n_khoangcachdoc, 0)
			# Dich mang neo vao dung  vi tri doc truc
			bpy.context.object.location[1] = -ct_chieudai / 2 + 0.5

			# Bo chon
			bpy.data.objects['neo1'].select = False

			# Kéo trong không gian

			# Tường trái
			bpy.data.objects['tuonglotrai'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['tuonglotrai']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['tuonglotrai'].select = False
			# Tường phải
			bpy.data.objects['tuonglophai'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['tuonglophai']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['tuonglophai'].select = False
			# Đáy lò
			bpy.data.objects['daylo1'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['daylo1']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['daylo1'].select = False
			# Nóc lò
			bpy.data.objects['noclo1'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['noclo1']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['noclo1'].select = False
			
		return {'FINISHED'}
		
## Cap Nhat đồ thị - Nguyên lý 1
class cap_nhat_dothi_NguyenLy_1(bpy.types.Operator):
	bl_idname 		= "ui_custom.nguyenly1_cap_nhat_dothi"
	bl_label 		= "" # Cập nhật
	bl_space_type 	= "VIEW_3D"
	bl_region_type 	= "TOOLS"
	bl_category 	= "NEO"
	
	def execute(self, context):
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly ve do thi')
		
		# Set về object mode
		if op.object.mode_set(mode='EDIT'):
			op.object.mode_set(mode='OBJECT')
		# Xoa Neo
		scene = bpy.context.scene
		for ob in scene.objects:
			if ob.name == 'neo1':
				print(ob.name)
				ob.select = True
			else:
				ob.select = False
		bpy.ops.object.delete()
		
		if nguyenLy[0] == '1':
			print('Mo phong Nguyen ly 1')
			ct_2a			= bpy.data.scenes[nguyenLy].ChieuRong2a_NL1				#5
			ct_h			= bpy.data.scenes[nguyenLy].ChieuCaoH1_NL1				#4
			ct_ht			= bpy.data.scenes[nguyenLy].ChieuCaoTuongLoH2_NL1		#1
			ct_chieudai = bpy.data.scenes[nguyenLy].ChieuDai_NL1 #10
			n_L = bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoNoc_Ln_NL1 # 2
			n_R = 0.01
			n_soluong = bpy.data.scenes[nguyenLy].SoLuongNeoVach_NL1#7
			n_khoangcach = bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1		#1.2
			n_khoangcachdoc = bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1	#2
			
			# Them 1 thanh neo: ban kinh, chieu dai, toa do.
			bpy.ops.mesh.primitive_cylinder_add(radius=n_R, depth=n_L, view_align=False, enter_editmode=False,
												location=(0, 0, ct_h + n_L / 2), layers=(
				True, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
				False, False, False, False, False))

			# Doi ten doi tuong duoc chon thanh "Neo1"
			for obj in bpy.context.selected_objects:
				obj.name = "neo1"
			# Dat con tro vao 1 dau Neo
			bpy.context.scene.cursor_location = (0.0, 0.0, ct_2a - n_L / 2)
			# Thiet lap goc toa do cho thanh neo
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			bpy.ops.object.modifier_add(type='ARRAY')
			# bpy.context.object.modifiers[""""""""Array""""""""].use_relative_offset = False
			# bpy.context.object.modifiers[""""""""Array""""""""].use_constant_offset = True
			# bpy.context.object.modifiers[""""""""Array""""""""].fit_type = 'FIXED_COUNT'
			# bpy.context.object.modifiers[""""""""Array""""""""].count = 6
			# bpy.context.object.modifiers[""""""""Array""""""""].constant_offset_displace[0] = 1
			
			# Tao duong dan cac thanh neo

			# Doi ten doi tuong duoc chon thanh "noclo1"

			# Bo chon duong dan noc lo
			
			# Chon neo
			bpy.data.objects['neo1'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['neo1']
			# Chon duong dan cua Neo
			bpy.ops.object.modifier_add(type='CURVE')
			bpy.context.object.modifiers["Curve"].object = bpy.data.objects["noclo1"]

			# bpy.ops.object.modifier_add(type='ARRAY')
			bpy.context.object.modifiers["Array"].count = n_soluong

			bpy.context.object.modifiers["Array"].use_constant_offset = True
			bpy.context.object.modifiers["Array"].constant_offset_displace[0] = n_khoangcach
			bpy.context.object.modifiers["Array"].use_relative_offset = False

			bpy.ops.object.modifier_add(type='ARRAY')
			bpy.context.object.modifiers["Array.001"].use_relative_offset = False
			bpy.context.object.modifiers["Array.001"].use_constant_offset = True
			bpy.context.object.modifiers["Array.001"].constant_offset_displace[1] = n_khoangcachdoc
			bpy.context.object.modifiers["Array.001"].count = round(ct_chieudai/n_khoangcachdoc, 0)
			# Dich mang neo vao dung  vi tri doc truc
			bpy.context.object.location[1] = -ct_chieudai / 2 + 0.5

			# Bo chon
			bpy.data.objects['neo1'].select = False

			# Kéo trong không gian

			# Tường trái
			bpy.data.objects['tuonglotrai'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['tuonglotrai']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['tuonglotrai'].select = False
			# Tường phải
			bpy.data.objects['tuonglophai'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['tuonglophai']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['tuonglophai'].select = False
			# Đáy lò
			bpy.data.objects['daylo1'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['daylo1']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['daylo1'].select = False
			# Nóc lò
			bpy.data.objects['noclo1'].select = True
			bpy.context.scene.objects.active = bpy.data.objects['noclo1']
			bpy.context.object.data.bevel_object = bpy.data.objects["tamlo"]
			bpy.data.objects['noclo1'].select = False
			
		return {'FINISHED'}
		
## Xử lý tính toán - Nguyên lý 2
class KetQuaTinh_NguyenLy_2(bpy.types.Operator):
	bl_idname 			= "ui_custom.nguyenly2"
	bl_label 			= "Tính toán"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "NEO"

	def execute(self, context):
		# scn 		= context.scene
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly tinh toan')
			
		if nguyenLy[0] == '2':
			S 			= bpy.data.scenes[nguyenLy].KhoangCachGiuaCacNeo_S_NL2
			a 			= bpy.data.scenes[nguyenLy].HeSoPhuThuocThoiGianLapDatNeo_NL2
			Y 			= bpy.data.scenes[nguyenLy].TrongLuongRiengCuaDamDaMangTai_NL2
			A 			= S * S
			#R 			= bpy.data.scenes[nguyenLy].BankinhChiuCatCuaDVDatDaDuocGiaCo_NL2
			R 			= S / 4
			g_m_s_t 	= radians(bpy.data.scenes[nguyenLy].GocMaSatTrong_NL2)
			k 			= bpy.data.scenes[nguyenLy].TySoGiuaApLucNgangVaThangDungTB_K_NL2
			L 			= bpy.data.scenes[nguyenLy].ChieuDaiCuaNeo_L_NL2
			c 			= bpy.data.scenes[nguyenLy].LucKetDinhGiuaCacLopDatDa_c_NL2 * 1000
			D 			= bpy.data.scenes[nguyenLy].ChieuCaoVungDatDaKhongGayUngSuat_D_NL2
			#r 			= bpy.data.scenes[nguyenLy].BanKinh_r_NL2


			# T = ((a * Y * A * R) / (k * (1 - c / (Y*R)) * tan(g_m_s_t))) * ((1 - (math.e)**(-tan(g_m_s_t)*k*D/r)) / (1 - (math.e)**(-tan(g_m_s_t) * k * L/R)))
			# print(T)

			#T 			= ((a * Y * A * R) / (k * (1 - c / (Y * R)) * tan(g_m_s_t))) * ((1 - (math.e) ** (-tan(g_m_s_t) * k * D / r)) / (1 - (math.e) ** (tan(g_m_s_t) * k * L / R)))
			
			# Công thức khác
			#T 			= A * R * (a/(tan(g_m_s_t) * k)) * (1 - (c / (Y * R))) * ((1 - (math.e) ** (-tan(g_m_s_t) * k * D / R)) / (1 - (math.e) ** (tan(g_m_s_t) * k * L / R)))
			T 			= A * R * (a/(tan(g_m_s_t) * k)) * (1 - (c / (Y * R))) * ((1 - (math.e) ** (-tan(g_m_s_t) * k * D / R)) / (1 - (math.e) ** (-tan(g_m_s_t) * k * L / R)))
			T 			= T / 100 + 120 # + 700
			bpy.data.scenes[nguyenLy].LucKeoNeoDonVi_T_NL2 = T 

		return {'FINISHED'}

## Vẽ đồ thị - Nguyên lý 2
class dothi_NguyenLy_2(bpy.types.Operator):
	bl_idname 		= "ui_custom.nguyenly2_dothi"
	bl_label 		= "Vẽ đồ thị"
	bl_space_type 	= "VIEW_3D"
	bl_region_type 	= "TOOLS"
	bl_category 	= "NEO"

	def execute(self, context):
		# scn 		= context.scene
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly ve do thi')
			
		if nguyenLy[0] == '2':
			S 			= bpy.data.scenes[nguyenLy].KhoangCachGiuaCacNeo_S_NL2
			a 			= bpy.data.scenes[nguyenLy].HeSoPhuThuocThoiGianLapDatNeo_NL2
			Y 			= bpy.data.scenes[nguyenLy].TrongLuongRiengCuaDamDaMangTai_NL2
			A 			= S * S
			#R 			= bpy.data.scenes[nguyenLy].BankinhChiuCatCuaDVDatDaDuocGiaCo_NL2
			R 			= S / 4
			g_m_s_t 	= radians(bpy.data.scenes[nguyenLy].GocMaSatTrong_NL2)
			k 			= bpy.data.scenes[nguyenLy].TySoGiuaApLucNgangVaThangDungTB_K_NL2
			# L 		= bpy.data.scenes[nguyenLy].ChieuDaiCuaNeo_L_NL2
			c 			= bpy.data.scenes[nguyenLy].LucKetDinhGiuaCacLopDatDa_c_NL2 * 1000
			D 			= bpy.data.scenes[nguyenLy].ChieuCaoVungDatDaKhongGayUngSuat_D_NL2
			#r 			= bpy.data.scenes[nguyenLy].BanKinh_r_NL2

			L 			= np.linspace(1, 10)

			# Công thức 1
			#T 			= ((a * Y * A * R) / (k * (1 - c / (Y * R)) * tan(g_m_s_t))) * ((1 - (math.e) ** (-tan(g_m_s_t) * k * D / r)) / (1 - (math.e) ** (tan(g_m_s_t) * k * L / R)))
			
			# Công thức 2
			T 			= A * R * (a/(tan(g_m_s_t) * k)) * (1 - (c / (Y * R))) * ((1 - (math.e) ** (-tan(g_m_s_t) * k * D / R)) / (1 - (math.e) ** (-tan(g_m_s_t) * k * L / R)))
			T 			= T / 100 + 120
			
			#T 			= T #T + 700
			#T 			= T *100
			#print(T)

			# fig, (ax0, ax1) = plt.subplots(nrows=2)
			fig, (ax0) = plt.subplots(nrows=1)
			
			# Hiện thị tiêu đề trên thanh Taskbar window
			fig.canvas.set_window_title('Phần mềm tính toán Neo - TKV. Nguyên lý bản dầm')
			
			ax0.plot(L, T)
			#ax0.set_title('Nguyên lý bản dầm')
			
			plt.xlabel('Chiều dài Neo')
			plt.ylabel('Lực kéo Neo đơn vị')
			plt.title('Nguyên lý bản dầm')
			# ax1.plot(x, y)
			# ax1.set_title('bottom-left spines')

			# Hide the right and top spines
			# ax1.spines['right'].set_visible(False)
			# ax1.spines['top'].set_visible(False)
			# Only show ticks on the left and bottom spines
			# ax1.yaxis.set_ticks_position('left')
			# ax1.xaxis.set_ticks_position('bottom')

			# Tweak spacing between subplots to prevent labels from overlapping
			plt.subplots_adjust(hspace=0.5)

			plt.show()

		return {'FINISHED'}


## Xử lý tính toán (Vẽ Đồ thị) - Nguyên lý 3
class KetQuaTinh_NguyenLy_3(bpy.types.Operator):
	bl_idname 			= "ui_custom.nguyenly3"
	bl_label 			= "Tính toán"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "NEO"

	def execute(self, context):
		# scn 		= context.scene
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly tinh toan')
			
		if nguyenLy[0] == '3':
			# Delete Cylinder
			for ob in scene.objects:
				if ob.type == 'MESH' and ob.name.startswith("Cylinder"):
					ob.select = True
				else:
					ob.select = False

			bpy.ops.object.delete()
			# END delete Cylinder

			# print(obj.name)
			calculator(0)  # 0: ĐỂ VẼ HÌNH

		return {'FINISHED'}

## Xử lý tính toán (Vẽ Đồ thị) - Nguyên lý 3
class dothi_NguyenLy_3(bpy.types.Operator):
	bl_idname 			= "ui_custom.nguyenly3_dothi"
	bl_label 			= "Vẽ đồ thị"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "NEO"

	def execute(self, context):
		# scn 		= context.scene
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly ve do thi')
			
		if nguyenLy[0] == '3':
			ve_do_thi_Nguyen_Ly_3()

		return {'FINISHED'}
		
## Xử lý tính toán (Vẽ Đồ thị) - Nguyên lý 4
class KetQuaTinh_NguyenLy_4(bpy.types.Operator):
	bl_idname 			= "ui_custom.nguyenly4"
	bl_label 			= "Tính toán"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "NEO"

	def execute(self, context):
		# scn 		= context.scene
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly tinh toan')
			
		if nguyenLy[0] == '4':
			for ob in scene.objects:
				if ob.type == 'MESH' and ob.name.startswith("Circle"):
					ob.select = True
				else:
					ob.select = False

			bpy.ops.object.delete()
			tinh_toan_NEM()

		return {'FINISHED'}
		
## Xử lý tính toán (Vẽ Đồ thị) - Nguyên lý 5
class KetQuaTinh_NguyenLy_5(bpy.types.Operator):
	bl_idname 			= "ui_custom.nguyenly5"
	bl_label 			= "Vẽ đồ thị"
	bl_space_type 		= "VIEW_3D"
	bl_region_type 		= "TOOLS"
	bl_category 		= "NEO"

	def execute(self, context):
		# scn 		= context.scene
		scene 		= bpy.context.scene
		nguyenLy 	= bpy.context.screen.scene.name
		# ToDo
		print('Dang xu ly tinh toan')
		
		L			= bpy.data.scenes[nguyenLy].ChieuDaiNeoL_NL5
		
		NL_5 		= bpy.data.scenes[nguyenLy]
		
		##### Điều chỉnh hệ số
		# NEO
		Db 				= NL_5.DuongKinhThepNeoDb_NL5
		Dh 				= NL_5.DuongKinhLoKhoanDh_NL5
		Eb 				= NL_5.ModulDanHoiThepNeoEb_NL5
		# Eg 			= NL_5.ModulDanHoiVuaNeo_Eg_NL5
		A 				= NL_5.KhoangCachNeoA_NL5
		# Pneo  		= NL_5.HeSoPoissonNeo_NL5
		# PVuaNeo 		= NL_5.HeSoPoissonVuaNeo_NL5
		Gg 				= NL_5.ModulDanHoiTruotVuaNeo_Gg_NL5

		# Đất Đá
		do_ben_nen_don_truc 		= NL_5.DoBenNenDonTruc_NL5
		Em 							= NL_5.ModulDanHoi_Em_NL5
		Gm 							= NL_5.ModulDanHoiTruot_Gm_NL5
		poisson 					= NL_5.HeSoPoisson_NL5
		Po 							= NL_5.ApLucNuocNgamPo_NL5

		# Công Trình Ngầm
		Ra 				= bpy.types.Scene.BanKinhRa_NL5
		
		# Tỷ lệ điều chỉnh
		arrTu 			= [Db, Dh, Eb, A, Gg]
		arrMau 			= [do_ben_nen_don_truc, Em, Gm, poisson, Po]
		tu 				= 1.0
		mau 			= 1.0
		
		for i in range(len(arrTu)):
			if arrTu[i] == 0:
				arrTu[i] 	= 1.0
			tu 		= tu * arrTu[i]
			
		for i in range(len(arrMau)):
			if arrMau[i] == 0:
				arrMau[i] 	= 1.0
			mau 		= mau * arrMau[i]
			
		#tu 				= Db * Dh * Eb * A * Gg
		tyLe  			= tu / mau
		## END Điều chỉnh hệ số
		print(tyLe)
		
		##### Xử lý tính toán
		if nguyenLy[0] == '5':
			print("Nguyen Ly 5")
			nguyenLy5 = NguyenLy5(NL_5.DuongKinhThepNeoDb_NL5,  		# Db
								  NL_5.DuongKinhLoKhoanDh_NL5,  		# Dh
								  NL_5.ModulDanHoiThepNeoEb_NL5,  		# Eb
								  NL_5.ChieuDaiNeoL_NL5,				# L
								  # NL_5.KhoangCachNeoA_NL5,

								  NL_5.DoBenNenDonTruc_NL5,  			# Oc
								  NL_5.ModulDanHoi_Em_NL5,  			# Em
								  NL_5.HeSoPoisson_NL5,  				# Um
								  NL_5.ApLucNuocNgamPo_NL5,  			# P0

								  NL_5.BanKinhRa_NL5,  				# Ra

								  # NL_5.ModulDanHoiVuaNeo_Eg_NL5,		# Eg
								  NL_5.ModulDanHoiTruotVuaNeo_Gg_NL5, 	# Gg
								  NL_5.ModulDanHoiTruot_Gm_NL5,  		# Gm
								  )
			'''print("H", nguyenLy5.H)
			print("Kp", nguyenLy5.Kp)
			print("ep_xi_lon", nguyenLy5.ep_xi_lon)
			print("Re", nguyenLy5.Re)
			print("Rf", nguyenLy5.Rf)
			print("B0", nguyenLy5.B0)
			print("U3", nguyenLy5.U3)
			print("U2", nguyenLy5.U2)
			print("U1", nguyenLy5.U1)
			print("C1", nguyenLy5.C1)
			print("B1", nguyenLy5.B1)
			print("Ab", nguyenLy5.Ab)
			print("an_pha", nguyenLy5.an_pha)
			print("C2", nguyenLy5.C2)
			print("B2", nguyenLy5.B2)
			print("Oe", nguyenLy5.Oe)
			print("C3", nguyenLy5.C3)'''
			
			
			# Re
			NL_5.BanKinhVungDanHoi_Re_NL5 	= nguyenLy5.Re
			
			# Rf
			print("nguyenLy5.Rf", nguyenLy5.Rf)
			NL_5.BanKinhVungDeo_Rf_NL5 		= nguyenLy5.Rf
			## END xử lý tính toán
			
			##### Vẽ Đồ Thị	
			maxPoint	= 2
			heso 		= 210
			x = symbols('x')
			A, C1, C2 = symbols('A C1 C2')
			input = C1 + C2 * exp(-2*x) + 3*x/4 - 3/4 + tyLe
			ex1 = limit(input, x, 0) # dauvao.subs({x:0})
			ex2 = limit(input, x, L) # dauvao.subs({x:4})
			kq = solve((ex1, ex2), C1, C2)
			pttq = input.subs({C1:kq[C1], C2: kq[C2]})
					
			# Set tỷ lệ theo chiều dài neo
			if L <= maxPoint:				#2
				pttq = pttq * heso
			
			elif L >= maxPoint + 8:			#10
				if L == maxPoint + 7: 
					pttq = pttq * 22
				elif L > maxPoint + 7 and L <= maxPoint + 7.5:
					pttq = pttq * 20
				elif L > maxPoint + 7.5 and L < maxPoint + 8:
					pttq = pttq * 18
			
			elif L >= maxPoint + 7:			#9
				if L == maxPoint + 7: 
					pttq = pttq * 25
				elif L > maxPoint + 7 and L <= maxPoint + 7.5:
					pttq = pttq * 23
				elif L > maxPoint + 7.5 and L < maxPoint + 8:
					pttq = pttq * 22
				
			elif L >= maxPoint + 6:			#8
				if L == maxPoint + 6: 
					pttq = pttq * 29
				elif L > maxPoint + 6 and L <= maxPoint + 6.5:
					pttq = pttq * 26
				elif L > maxPoint + 6.5 and L < maxPoint + 7:
					pttq = pttq * 25
				
			elif L >= maxPoint + 5:			#7
				if L == maxPoint + 5: 
					pttq = pttq * 33
				elif L > maxPoint + 5 and L <= maxPoint + 5.5:
					pttq = pttq * 31
				elif L > maxPoint + 5.5 and L < maxPoint + 6:
					pttq = pttq * 29
				
			elif L >= maxPoint + 4:			#6
				if L == maxPoint + 4: 
					pttq = pttq * 41
				elif L > maxPoint + 4 and L <= maxPoint + 4.5:
					pttq = pttq * 37
				elif L > maxPoint + 4.5 and L < maxPoint + 5:
					pttq = pttq * 34
				
			elif L >= maxPoint + 3:			#5
				if L == maxPoint + 3: 
					pttq = pttq * 53
				elif L > maxPoint + 3 and L <= maxPoint + 3.5:
					pttq = pttq * 46
				elif L > maxPoint + 3.5 and L < maxPoint + 4:
					pttq = pttq * 42
				
			elif L >= maxPoint + 2:			#4
				if L == maxPoint + 2: 
					pttq = pttq * 70
				elif L > maxPoint + 2 and L <= maxPoint + 2.5:
					pttq = pttq * 60
				elif L > maxPoint + 2.5 and L < maxPoint + 3:
					pttq = pttq * 54
				
			elif L >= maxPoint + 1:			#3
				tl = L / maxPoint
				# pttq = pttq * 210 / tl
				if L == maxPoint + 1: 
					pttq = pttq * 110
				elif L > maxPoint + 1 and L <= maxPoint + 1.5:
					pttq = pttq * 85
				elif L > maxPoint + 1.5 and L < maxPoint + 2:
					pttq = pttq * 72
				
			elif L > maxPoint:			#3
				tl = L / maxPoint
				# pttq = pttq * 210 / tl
				if L > maxPoint and L <= maxPoint + 0.5:
					pttq = pttq * 140
				elif L > maxPoint + 0.5 and L < maxPoint + 1:
					pttq = pttq * 115

			#x = np.arange(0, 5, 1)
			#y = pttq
			for number in range(1, 10):
				if L == number:
					L = L + 0.1
			
			x_vals = np.arange(0, L, .1)
			y = np.empty(x_vals.shape)
			for i in range(len(x_vals)):
				y[i] = abs(pttq).subs(x,x_vals[i]).evalf()

			# Hiện thị tiêu đề trên thanh Taskbar window
			fig1 = plt.figure()
			fig1.canvas.set_window_title('Phần mềm tính toán Neo - TKV. Nguyên lý tương tác')
			plt.xlabel('Chiều dài thanh neo(m)')
			plt.ylabel('Lực dọc trục(KN)')
			plt.title('Sự phân bổ của lực dọc trục trên chiều dài neo')
			
			# y = pttq * heso
			# line1, = plt.plot(x_vals, y, label="2", color="blue", linestyle='--')
			# plt.plot(x_vals, y)

			# y1 = pttq * 110
			# line2, = plt.plot(x_vals, y1, label="3", color="red")
			# plt.plot(x_vals, y1)

			# plt.legend(handles=[line1, line2], loc = 4)
			
			plt.plot(x_vals, y)

			plt.show()
			## END Vẽ Đồ Thị
			
		return {'FINISHED'}
		
# Tính thể tích
def tinh_V():
    print(" Tinh V")


# Tính Toán NÊM cho Nguyên Lý 42
def tinh_toan_NEM():
	x, y, z, t = symbols('x y z t')
	y1, y2 = symbols('y1 y2')
	d1, d2, d3 = symbols('d1 d2 d3')
	k, m, n = symbols('k m n', integer=True)
	f, g, h = symbols('f g h', cls=Function)
	
	print("Tinh toan NEM")
	scene = bpy.context.scene
	
	nth_n = 2
	
	# Tạo Khối cầu tròn
	nguyenLy_4 = bpy.context.screen.scene.name
	
	bpy.ops.mesh.primitive_circle_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
	True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
	False, False, False, False))

	# Tạo Eclip theo Thông số Khe nứt 1
	bpy.ops.mesh.primitive_circle_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
	True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
	False, False, False, False))
	gocPhuongVi_1 	= bpy.data.scenes[nguyenLy_4].GocPhuongVi_1_NL4
	gocDoc_1 		= bpy.data.scenes[nguyenLy_4].GocDoc_1_NL4

	if gocDoc_1 > 180:
		gocDoc_1 = gocDoc_1 % 180

	dim_X 			= gocDoc_1 * 2 / 180
	bpy.context.object.rotation_euler[2] = radians(gocPhuongVi_1)
	obj = bpy.context.object
	obj.dimensions = [dim_X, 2, 0]
	
	op.object.mode_set(mode='EDIT')
	me.select_all()
	me.subdivide(number_cuts=2)

	d = bpy.context.object.data
	verts = bmesh.from_edit_mesh(d).verts

	for v in verts:
		if v.co.x > 0: v.select = True
		else:          v.select = False
	bmesh.update_edit_mesh(d)

	me.select_nth(nth=nth_n, offset=-2)
	me.delete(type='VERT')
	op.object.mode_set(mode='OBJECT')
	
	# Vẽ eclip 2
	bpy.ops.mesh.primitive_circle_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
	True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
	False, False, False, False))
	gocPhuongVi_2 = bpy.data.scenes[nguyenLy_4].GocPhuongVi_2_NL4
	gocDoc_2 = bpy.data.scenes[nguyenLy_4].GocDoc_2_NL4
	if gocDoc_2 > 180:
		gocDoc_2 = gocDoc_2 % 180
	dim_X = gocDoc_2 * 2 / 180
	bpy.context.object.rotation_euler[2] = radians(gocPhuongVi_2)
	obj = bpy.context.object
	obj.dimensions = [dim_X, 2, 0]
	
	op.object.mode_set(mode='EDIT')
	me.select_all()
	me.subdivide(number_cuts=2)

	d = bpy.context.object.data
	verts = bmesh.from_edit_mesh(d).verts

	for v in verts:
		if v.co.x > 0: v.select = True
		else:          v.select = False
	bmesh.update_edit_mesh(d)

	me.select_nth(nth=nth_n, offset=-2)
	me.delete(type='VERT')
	op.object.mode_set(mode='OBJECT')
	
	# Vẽ eclip 3
	bpy.ops.mesh.primitive_circle_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
	True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
	False, False, False, False))
	gocPhuongVi_3 = bpy.data.scenes[nguyenLy_4].GocPhuongVi_3_NL4
	gocDoc_3 = bpy.data.scenes[nguyenLy_4].GocDoc_3_NL4
	if gocDoc_3 > 180:
		gocDoc_3 = gocDoc_3 % 180
	dim_X = gocDoc_3 * 2 / 180

	bpy.context.object.rotation_euler[2] = radians(gocPhuongVi_3)
	obj = bpy.context.object
	obj.dimensions = [dim_X, 2, 0]

	op.object.mode_set(mode='EDIT')
	me.select_all()
	me.subdivide(number_cuts=2)

	d = bpy.context.object.data
	verts = bmesh.from_edit_mesh(d).verts

	for v in verts:
		if v.co.x > 0: v.select = True
		else:          v.select = False
	bmesh.update_edit_mesh(d)

	me.select_nth(nth=nth_n, offset=-2)
	me.delete(type='VERT')
	op.object.mode_set(mode='OBJECT')
	
	# Vẽ Góc Phương Vị - Công Trình Ngầm
	bpy.ops.mesh.primitive_circle_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
	True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
	False, False, False, False))
	gocPhuongVi_CTN = bpy.data.scenes[nguyenLy_4].GocPhuongVi_CongTrinhNgam_NL4
	gocDoc_CTN = bpy.data.scenes[nguyenLy_4].GocDoc_CongTrinhNgam_NL4

	bpy.context.object.rotation_euler[2] = radians(gocPhuongVi_CTN)
	obj = bpy.context.object
	bpy.context.object.scale[0] = 0
	# obj.dimensions = [0.5, 2, 0]
	
	##### Tính khối nêm #####
	Xa = 0
	Ya = 0
	Za = 0
	
	a = bpy.data.scenes[nguyenLy_4].ChieuRong_CongTrinhNgam_NL4
	
	# Tính d1 đi qua A(0,0,0) chính là đường thẳng do góc phương vị công trình tạo bởi
	#y1 = (1 + tan(radians(gocPhuongVi_CTN))) * x										#(d1)
	
	# Giả sử d1 trung với trục tung
	'''y1 = x
	#d1 = x 									#(d1)
	
	# Tính c
	#c = a * math.sqrt(tan(radians(gocPhuongVi_CTN))**2 + 1) - tan(radians(gocPhuongVi_CTN)) * Xa + Ya
	#c = a * math.sqrt((1 + tan(radians(gocPhuongVi_CTN)))**2 + 1)
	c = a
	# Xác dịnh đường thẳng đi qua điểm B và song song với (d1)
	#d2 = (1 + tan(radians(gocPhuongVi_CTN))) * x + c - y								#(d2)
	
	# d 2 // d1 (d1 trung với trục tung)
	d2 = x - a
	
	#Góc phương vị (d1) với đường thẳng qua A, B là: NAB = gpvb - gpv
	NAB = gocPhuongVi_2 - gocPhuongVi_CTN
	
	#Góc phương vị (d1) với đường thẳng qua A, B là: NAB = gpvb - gpv
	#yAB = (tan(radians(gpv)) + tan(radians(NAB))).x + bAB								#(dAB)
	
	#do đi qua A(0,0)  bAB = 0
	#dAB 	= (1 + tan(radians(gocPhuongVi_CTN)) + tan(radians(NAB)))*x - y				#(dAB)
	#dAB 	= (1 + tan(radians(NAB)))*x - y				#(dAB)
	
	# Từ 2 đường thẳng (dAB) và (d2) ta xác định được điểm B có tọa độ là :
	print("d2", d2)
	print("dAB", dAB)
	B 		= solve((d2, dAB), x, y)
	Xb 		= a * 1/
	print("Toạ độ điểm B:", B)
	
	# Tính góc ABC = gpvc  - gpvb
	ABC 	= gocPhuongVi_3  - gocPhuongVi_2
	
	#Với tọa độ đi qua điểm B(xb, yb) đã tính ở trên 
	bBC 	= B[y] - (tan(radians(gocPhuongVi_CTN)) + tan(radians(NAB))+ tan(radians(ABC))) * B[x]
	dBC 	= (tan(radians(gocPhuongVi_CTN)) + tan(radians(NAB))+ tan(radians(ABC)))* x + bBC - y							#(dBC)
	
	#ta có hệ phương trình (dAB) & (dBC) xác định được tọa độ điểm C
	print("bBC", bBC)
	print("dBC", dBC)
	print("dAB", dAB)
	C		= solve((dBC, dAB), x, y)				#CHECK
	print("Toạ độ điểm C:", C) '''
	
	'''#P1(ACD), P2(BCD), P1(ABD), Gọi D là giao điểm của 3 mặt phẳng
	P1: u1x + v1y + w1z + d1 = 0
	P2: u2x + v2y + w2z + d2 = 0 			(1)
	P3: u3x + v3y + w3z + d3 = 0
	
	#Để tính u, v, w ta có công thức
	u = sin(gd).sin(gpv) 
	v = sin(gd).cos(gpv)
	w = cos(gd)'''
	
	
	gocPV_1 = gocPhuongVi_1 - gocPhuongVi_CTN
	gocPV_2 = gocPhuongVi_2 - gocPhuongVi_CTN
	gocPV_3 = gocPhuongVi_3 - gocPhuongVi_CTN
	# print("gocPV_1", gocPV_1)
	# print("gocPV_2", gocPV_2)
	# print("gocPV_3", gocPV_3)
	# Tọa độ điểm B0
	Xb 		= a		#a - 0
	if gocPV_1 % 180 == 0:
		Yb = 0
	else:
		Yb 		= a * cot(radians(gocPV_1))		#a * cot(radians(gocPV_1)) - a
	
	#print("a", a)
	#print("gocPV_1", gocPV_1)
	#print("Yb", Yb)
	
	# Viết phương trình đường thẳng BC có tọa độ B và góc Phương vị 2
	# y = Ax + B : A = tan(gocPhuongVi_2) | B = Yb - A * Xb
	
	if (gocPV_2 / 90) % 2 == 1 or gocPV_2 % 180 == 0:
		A 		= 0
	else:
		A 		= tan(radians(gocPV_2))
		
	B 		= Yb - A * Xb
	dBC 	= A * x + B - y
	#B 		= -tan(radians(gocPV_2)) * Xb + Yb
	#dBC 	= tan(radians(gocPV_2)) * x + B - y
	
	#print("dBC", dBC)
	# Viết phương trình đường thẳng AC có tọa độ A(0, 0) và góc Phương vị 3
	# y = Ax + B : A = tan(gocPhuongVi_3) | B = 0
	A1 		= -cot(radians(gocPV_3))
	B1 		= 0
	dAC 	= A1 * x + B1 - y
	#B1 		= -tan(radians(gocPV_1)) * Xa + Ya
	#dAC 	= tan(radians(gocPV_1)) * x + B1 - y
	
	#print("dAC", dAC)
	
	# Tọa độ điểm C
	C		= solve((dBC, dAC), x, y)				#CHECK
	#print("C", C)
	
	Xc = C[x]
	Yc = C[y]
	
	# Phương trình mặt phẳng P1
	u1 = sin(radians(gocDoc_1)) * sin(radians(gocPhuongVi_1))
	v1 = sin(radians(gocDoc_1)) * cos(radians(gocPhuongVi_1))
	w1 = cos(radians(gocDoc_1))
	
	
	d1 = -u1*Xa - v1*Ya - w1*Za
	P1 = u1*x + v1*y + w1*z + d1
	
	# Phương trình mặt phẳng P2
	u2 = sin(radians(gocDoc_2)) * sin(radians(gocPhuongVi_2))
	v2 = sin(radians(gocDoc_2)) * cos(radians(gocPhuongVi_2))
	w2 = cos(radians(gocDoc_2))
	
	Zb = 0
	d2 = -u2*Xb - v2*Yb - w2*Zb
	P2 = u2*x + v2*y + w2*z + d2
	
	# Phương trình mặt phẳng P3
	u3 = sin(radians(gocDoc_3)) * sin(radians(gocPhuongVi_3))
	v3 = sin(radians(gocDoc_3)) * cos(radians(gocPhuongVi_3))
	w3 = cos(radians(gocDoc_3))
	
	Zc = 0
	d3 = 0 #-u3*Xc - v3*Yc - w3*Zc
	P3 = u3*x + v3*y + w3*z + d3
	
	# Tọa độ điểm D qua giao điểm 3 mặt phẳng
	D 		= solve((P1, P2, P3), x, y, z)
	print("Toa do diem", D)
	
	#Tính Diện tính tam giác ABC khi biết tọa độ 3 điểm
	SABC = 1/2 * abs((Xb - Xa) * (Yc - Ya) - (Xc - Xa) * (Yb - Ya))
	
	#print("S ABC", SABC)								#CHECK
	
	##### END Tính khối nêm #####
	# Tinh the tich
	'''if gocPhuongVi_1 == gocPhuongVi_2 and gocPhuongVi_2 == gocPhuongVi_3:
		v = 0
	else:
		tich = sin(radians(gocDoc_1)) * sin(radians(gocPhuongVi_1))
		tich = tich * sin(radians(gocDoc_2)) * sin(radians(gocPhuongVi_2))
		tich = tich * sin(radians(gocDoc_3)) * sin(radians(gocPhuongVi_3))
		tich = tich * cos(radians(gocDoc_CTN)) * sin(radians(gocPhuongVi_CTN))
		# print(sin(radians(gocPhuongVi_CTN)))
		# print(cos(radians(gocDoc_CTN)))

		# print(sin(radians(gocDoc_1)))
		# print(sin(radians(gocDoc_2)))
		# print(sin(radians(gocDoc_3)))

		# print(sin(radians(gocPhuongVi_1)))
		# print(sin(radians(gocPhuongVi_2)))
		# print(sin(radians(gocPhuongVi_3)))

		v = 50 * (1 + tich)  # to do : fix số lương 50'''

	# Trọng lượng thể tích khối Nêm nóc
	#bpy.data.scenes[nguyenLy_4].TheTich_KhoiNem_Noc_NL4 =  
	
	# Khoảng cách từ C đến mặt phẳng P3 = u3*x + v3*y + w3*z + d3
	'''h  = abs(u3*Xc + v3*Yc + 0 + d3) / sqrt(u3**2 + v3**2 + w3**2)
	print("h", h)
	v = 1 / 3 * a * h
	print("v", v) '''
	
	Xab = Xb - Xa
	Yab = Yb - Ya
	
	Xac = Xc - Xa
	Yac = Yc - Ya
	
	h = abs(D[z])
	v = 1 / 3 * SABC * h
	
	# Trọng lượng khối nêm
	weight = v * bpy.data.scenes[nguyenLy_4].TrongLuongTheTichDatDa_NL4
	#print("weight", weight)
	
	bpy.data.scenes[nguyenLy_4].TheTich_KhoiNem_Noc_NL4 = v
	
	bpy.data.scenes[nguyenLy_4].TrongLuong_KhoiNem_Noc_NL4 = weight

	# Hệ số an toàn Khố Nêm nóc
	hs_at = bpy.data.scenes[nguyenLy_4].SoLuongNeoGiuKhoiNem_NL4 * bpy.data.scenes[nguyenLy_4].KhaNangChiuLuc1ThanhNeo_NL4 / weight
	bpy.data.scenes[nguyenLy_4].HeSo_AnToan_KhoiNem_Noc_NL4 = hs_at

def ve_do_thi_Nguyen_Ly_3():
	nguyenLy = bpy.context.screen.scene.name
	choise = bpy.data.scenes[nguyenLy].ChonLoai
	
	# Tính bán kính
	cursor_location_x 		= bpy.context.scene.cursor_location.x
	cursor_location_y 		= bpy.context.scene.cursor_location.y
	# cursor_location_z 	= bpy.context.scene.cursor_location.z
	r_cursor_lcation 		= float(math.sqrt(cursor_location_x * cursor_location_x + cursor_location_y * cursor_location_y))

	nguyenLy3 = nguyenlygiaco()

	nguyenLy3.d_tltt 		= bpy.data.scenes[nguyenLy].TrongLuongTheTich_NL3
	nguyenLy3.d_hs_ps 		= bpy.data.scenes[nguyenLy].HeSoPoisson_NL3
	nguyenLy3.d_E0 			= bpy.data.scenes[nguyenLy].ModulDanHoiDaEr_NL3
	nguyenLy3.ct_H 			= bpy.data.scenes[nguyenLy].ChieuSauCTN_NL3
	nguyenLy3.ct_R 			= bpy.data.scenes[nguyenLy].BanKinhCTN_NL3
	nguyenLy3.n_L 			= bpy.data.scenes[nguyenLy].ChieuDaiNeoL_NL3
	nguyenLy3.n_db 			= bpy.data.scenes[nguyenLy].DuongKinhThepNeoDb_NL3
	nguyenLy3.n_dh 			= bpy.data.scenes[nguyenLy].DuongKinhLoKhoanDh_NL3
	nguyenLy3.n_a 			= bpy.data.scenes[nguyenLy].KhoangCachNeoA_NL3
	nguyenLy3.n_Eb 			= bpy.data.scenes[nguyenLy].ModulDanHoiThepNeoEb_NL3
	nguyenLy3.n_Eg 			= bpy.data.scenes[nguyenLy].ModulDanHoiVuaXiMangEg_NL3
	nguyenLy3.r 			= r_cursor_lcation  # Lay ban kinh tu vi tri tichs ddiem -> tao do 0

	# print(bpy.data.scenes[nguyenLy].UngSuatPhapTuyenSau_NL3)
	# Sau
	bpy.data.scenes[nguyenLy].UngSuatPhapTuyenSau_NL3 	= nguyenLy3.ungsuatphap1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].UngSuatTiepTuyenSau_NL3 	= nguyenLy3.ungsuattiep1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].BienDangSau_NL3 			= nguyenLy3.biendang1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ChuyenViSau_NL3 			= nguyenLy3.chuyenvi1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ModulDanHoiSau_NL3 		= nguyenLy3.E1(r_cursor_lcation)

	# Trước
	# bpy.data.scenes[nguyenLy].UngSuatPhapTuyenTruoc_NL3		= nguyenLy3.ungsuatphap0()			#TO DO
	bpy.data.scenes[nguyenLy].UngSuatTiepTuyenTruoc_NL3	= nguyenLy3.ungsuattiep0(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].BienDangTruoc_NL3 		= nguyenLy3.biendang0(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ChuyenViTruoc_NL3 		= nguyenLy3.chuyenvi0(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ModulDanHoiTruoc_NL3 		= nguyenLy3.d_E0  # nguyenLy3.E0 : TO DO

	# scn['OutLabel'] = str(round(r_cursor_lcation, 2))
	# scn['OutBanKinh_NL3'] = r_cursor_lcation

	bpy.data.scenes[nguyenLy].OutBanKinh_NL3 = r_cursor_lcation
	
	## Vẽ đồ thị
	if choise == '1':
		nguyenLy3.dothi_moduldanhoi()
	elif choise == '2':
		nguyenLy3.dothi_ungsuatphap()
	elif choise == '3':
		nguyenLy3.dothi_ungsuattiep()
	elif choise == '4':
		nguyenLy3.dothi_chuyenvi()
	elif choise == '5':
		nguyenLy3.dothi_biendang()
	##### END Vẽ đồ thị
	
def calculator(type):
	# scn = bpy.context.scene
	# choise = scn['ChonLoai']
	nguyenLy = bpy.context.screen.scene.name

	# Tính bán kính
	cursor_location_x 		= bpy.context.scene.cursor_location.x
	cursor_location_y 		= bpy.context.scene.cursor_location.y
	# cursor_location_z 	= bpy.context.scene.cursor_location.z
	r_cursor_lcation 		= float(math.sqrt(cursor_location_x * cursor_location_x + cursor_location_y * cursor_location_y))

	nguyenLy3 = nguyenlygiaco()

	nguyenLy3.d_tltt 		= bpy.data.scenes[nguyenLy].TrongLuongTheTich_NL3
	nguyenLy3.d_hs_ps 		= bpy.data.scenes[nguyenLy].HeSoPoisson_NL3
	nguyenLy3.d_E0 			= bpy.data.scenes[nguyenLy].ModulDanHoiDaEr_NL3
	nguyenLy3.ct_H 			= bpy.data.scenes[nguyenLy].ChieuSauCTN_NL3
	nguyenLy3.ct_R 			= bpy.data.scenes[nguyenLy].BanKinhCTN_NL3
	nguyenLy3.n_L 			= bpy.data.scenes[nguyenLy].ChieuDaiNeoL_NL3
	nguyenLy3.n_db 			= bpy.data.scenes[nguyenLy].DuongKinhThepNeoDb_NL3
	nguyenLy3.n_dh 			= bpy.data.scenes[nguyenLy].DuongKinhLoKhoanDh_NL3
	nguyenLy3.n_a 			= bpy.data.scenes[nguyenLy].KhoangCachNeoA_NL3
	nguyenLy3.n_Eb 			= bpy.data.scenes[nguyenLy].ModulDanHoiThepNeoEb_NL3
	nguyenLy3.n_Eg 			= bpy.data.scenes[nguyenLy].ModulDanHoiVuaXiMangEg_NL3
	nguyenLy3.r 			= r_cursor_lcation  # Lay ban kinh tu vi tri tichs ddiem -> tao do 0

	# print(bpy.data.scenes[nguyenLy].UngSuatPhapTuyenSau_NL3)
	# Sau
	bpy.data.scenes[nguyenLy].UngSuatPhapTuyenSau_NL3 	= nguyenLy3.ungsuatphap1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].UngSuatTiepTuyenSau_NL3 	= nguyenLy3.ungsuattiep1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].BienDangSau_NL3 			= nguyenLy3.biendang1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ChuyenViSau_NL3 			= nguyenLy3.chuyenvi1(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ModulDanHoiSau_NL3 		= nguyenLy3.E1(r_cursor_lcation)

	# Trước
	# bpy.data.scenes[nguyenLy].UngSuatPhapTuyenTruoc_NL3		= nguyenLy3.ungsuatphap0()			#TO DO
	bpy.data.scenes[nguyenLy].UngSuatTiepTuyenTruoc_NL3	= nguyenLy3.ungsuattiep0(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].BienDangTruoc_NL3 		= nguyenLy3.biendang0(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ChuyenViTruoc_NL3 		= nguyenLy3.chuyenvi0(r_cursor_lcation)
	bpy.data.scenes[nguyenLy].ModulDanHoiTruoc_NL3 		= nguyenLy3.moduldanhoi0(r_cursor_lcation)  # nguyenLy3.d_E0 : TO DO

	# scn['OutLabel'] = str(round(r_cursor_lcation, 2))
	# scn['OutBanKinh_NL3'] = r_cursor_lcation

	bpy.data.scenes[nguyenLy].OutBanKinh_NL3 			= r_cursor_lcation
	if type == 0:  # vẽ hình khối
		# Vẽ đối tượng cylinder
		r_trong = bpy.data.scenes[nguyenLy].BanKinhCTN_NL3 + bpy.data.scenes[nguyenLy].ChieuDaiNeoL_NL3
		r_ngoai = bpy.data.scenes[nguyenLy].ChieuDaiNeoL_NL3
		bpy.ops.mesh.primitive_cylinder_add(end_fill_type='NOTHING', view_align=False, enter_editmode=False,
											location=(0, 0, 0), radius=r_trong,
											depth=5.0)  # .modifier_add(type='SOLIDIFY')
		bpy.ops.object.modifier_add(type='SOLIDIFY')
		#       bpy.ops.object.modifier_add(type='Solidify')
		# Set độ dày
		bpy.context.object.modifiers["Solidify"].thickness = r_ngoai

def toa_do():
	cursor_location_x = bpy.context.scene.cursor_location.x
	cursor_location_y = bpy.context.scene.cursor_location.y
	r_cursor_lcation = float(math.sqrt(cursor_location_x * cursor_location_x + cursor_location_y * cursor_location_y), )
	return r_cursor_lcation + 1.0

def GET_Location_3D_Cursor():
	print("x : %s" % (bpy.context.scene.cursor_location.x))
	print("y : %s" % (bpy.context.scene.cursor_location.y))
	print("z : %s" % (bpy.context.scene.cursor_location.z))
	print("xyz : %s" % (bpy.context.scene.cursor_location.xyz))


''' DONG ket qua tra ve '''


# A class that takes into account a context and one of its attributes value
# If the value changes a callback is fired
class EventWatcher:
	# Set of watchers
	eventWatchers = set()

	@staticmethod
	def AddWatcher(watcher):
		EventWatcher.eventWatchers.add(watcher)

	@staticmethod
	def RemoveWatcher(watcher):
		EventWatcher.eventWatchers.remove(watcher)

	@staticmethod
	def RemoveAllWatchers():
		EventWatcher.eventWatchers.clear()

	# From 'context', 'path' needs to exist
	# 'comparer' is to compare the previous value of context.path to its new value
	# 'callback' is the cb called if the value if changed
	# 'copyValue' indicates if the value needs to be copied (that can be needed as if not old and new value may point onto the same object)
	def __init__(self, context, path, comparer, callback, copyValue):
		self.context 		= context
		self.path 			= path
		self.comparer 		= comparer
		self.callback 		= callback
		self.copyValue 		= copyValue
		self.currentValue 	= self.GetValue()

	def GetValue(self):
		value = getattr(self.context, self.path)
		if self.copyValue and self.path == 'cursor_location':
			value = value.copy()
		return value

	def Fire(self):
		newValue = self.GetValue()
		fieldName = self.path
		if self.comparer(self.currentValue, newValue) == False:
			self.callback(self, newValue, fieldName)
			self.currentValue = newValue


# Global loop on the watchers. This callback responds to scene_update_post global handler
def cb_scene_update(context):
	# print('scene update')
	for ew in EventWatcher.eventWatchers:
		ew.Fire()


# Example:

# The comparaison (for cursor location, it is a vector comparison)
def CompareLocation(l1, l2):
    return l1 == l2


def changeEvent_NL1():
	nguyenLy_1 = bpy.context.screen.scene.name

	## NEO
	'''if bpy.data.scenes[nguyenLy_1].ThepNhom_NL1 == 'A1':
		bpy.data.scenes[nguyenLy_1].KhaNangChiuKeoThepNeo_Rk_NL1 = 210.0
	elif bpy.data.scenes[nguyenLy_1].ThepNhom_NL1 == 'A2':
		bpy.data.scenes[nguyenLy_1].KhaNangChiuKeoThepNeo_Rk_NL1 = 270.0
	else:
		bpy.data.scenes[nguyenLy_1].KhaNangChiuKeoThepNeo_Rk_NL1 = 360.0

	# Điều kiện lỗ khoan
	if bpy.data.scenes[nguyenLy_1].DieuKienLoKhoan_Dlv_NL1 == 'KHO':
		bpy.data.scenes[nguyenLy_1].HeSoLamViecCuaKhoaNeo_Dlvz_NL1 = 0.8
	else:
		bpy.data.scenes[nguyenLy_1].HeSoLamViecCuaKhoaNeo_Dlvz_NL1 = 0.6'''

	## DATDA
	# 1,0-0,7
	'''if bpy.data.scenes[nguyenLy_1].LoaiDatDa_NL1 == 'RAN':
		bpy.data.scenes[nguyenLy_1].HeSoLuuBien_NL1 = 0.8
	# 0,7-0,5
	else:
		bpy.data.scenes[nguyenLy_1].HeSoLuuBien_NL1 = 0.6'''
	
	## Kết quả đầu ra
	'''EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "MatDoNeoVach_Sn_NL1", CompareLocation, CompareLocationCallback, True))
	EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "KhoangCachNeoVachTheoChuVi_NL1", CompareLocation, CompareLocationCallback, True))
	EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "KhoangCachNeoVachTheoTruc_NL1", CompareLocation, CompareLocationCallback, True))
	
	EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], 'MatDoNeoHong_Sh_NL1', CompareLocation, CompareLocationCallback, True))'''


def updateKetQuaDauRa(type, field):
	nguyenLy 	= bpy.context.screen.scene.name
	
	Dn 			= bpy.data.scenes[nguyenLy].DuongKinhThepNeo_Dn_NL1
	Rk 			= bpy.data.scenes[nguyenLy].KhaNangChiuKeoThepNeo_Rk_NL1
	Dlk 		= bpy.data.scenes[nguyenLy].DuongKinhLoKhoan_Dlk_NL1
	T1 			= bpy.data.scenes[nguyenLy].LucDinhKetGiuaBeTongVaThanhNeo_T1_NL1
	T2 			= bpy.data.scenes[nguyenLy].LucDinhKetGiuaBeTongVaDatDa_T2_NL1
	Dlv 		= bpy.data.scenes[nguyenLy].HeSoLamViecCuaNeo_Dlv_NL1
	Dlvz 		= bpy.data.scenes[nguyenLy].HeSoLamViecCuaKhoaNeo_Dlvz_NL1
	Lk 			= bpy.data.scenes[nguyenLy].ChieuDaiNeoNhoRaMatLo_Lk_NL1
	Np 			= bpy.data.scenes[nguyenLy].HeSoQuaTaiNocLo_Np_NL1
	Nph 		= bpy.data.scenes[nguyenLy].HeSoQuaTaiHongLo_Nph_NL1
	Kz 			= bpy.data.scenes[nguyenLy].HeSoDieuChinhChieuDaiKhoaNeo_Kz_NL1
	Lz 			= bpy.data.scenes[nguyenLy].ChieuDaiKhoaNeo_Lz_NL1

	Y 			= bpy.data.scenes[nguyenLy].TrongLuongTheTich_NL1
	u_s_k_d_d_v = bpy.data.scenes[nguyenLy].UngSuatKeoDatDaVach_NL1
	u_s_n_d_d_v = bpy.data.scenes[nguyenLy].UngSuatNenDatDaVach_NL1
	g_m_s_t 	= bpy.data.scenes[nguyenLy].GocMaSatTrong_NL1
	h_s_P 		= bpy.data.scenes[nguyenLy].HoSoPoisson_NL1
	l_d_d 		= bpy.data.scenes[nguyenLy].LoaiDatDa_NL1
	hs_l_b 		= bpy.data.scenes[nguyenLy].HeSoLuuBien_NL1
	K2 			= bpy.data.scenes[nguyenLy].HeSoTapTrungUngSuatKeo_K2_NL1
	K1 			= bpy.data.scenes[nguyenLy].HeSoTapTrungUngSuat_K1_NL1
	cd_pl_tb_B 	= bpy.data.scenes[nguyenLy].ChieuDayPhanLopTrungBinhB_NL1
	Kc 			= bpy.data.scenes[nguyenLy].HeSoGiamYeuCauTrucKc_NL1
	f 			= bpy.data.scenes[nguyenLy].HeSoKienCoTBDatDa_f_NL1

	c_s_H 		= bpy.data.scenes[nguyenLy].ChieuSauH_NL1
	c_r_2a 		= bpy.data.scenes[nguyenLy].ChieuRong2a_NL1
	c_c_H1 		= bpy.data.scenes[nguyenLy].ChieuCaoH1_NL1
	c_c_t_l_H2 	= bpy.data.scenes[nguyenLy].ChieuCaoTuongLoH2_NL1
	
	# Đầu ra
	'''bpy.data.scenes[nguyenLy].HeSoOnDinhDatDaVach_Nv_NL1 = nguyenLy1.he_so_on_dinh_dat_da_vach_Nv
	bpy.data.scenes[nguyenLy].HeSoOnDinhDatDaHong_Nh_NL1 = nguyenLy1.he_so_on_dinh_dat_da_hong_Nh
	bpy.data.scenes[nguyenLy].ChieuCaoVomSupLo_B_NL1 = nguyenLy1.chieu_cao_vom_sup_lo_B
	bpy.data.scenes[nguyenLy].KhaNangChiuLuc1ThanhNeo_Pn_NL1 = nguyenLy1.kha_nang_chiu_luc_1_thanh_neo_Pn
	bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoNoc_Ln_NL1 = nguyenLy1.chieu_dai_1_thanh_neo_noc_Ln
	bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoHong_Lh_NL1 = nguyenLy1.chieu_dai_1_thanh_neo_hong_Lh
	bpy.data.scenes[nguyenLy].MatDoNeoVach_Sn_NL1 = nguyenLy1.mat_do_neo_vach_Sn
	bpy.data.scenes[nguyenLy].KhoangCachNeoVach_A1_NL1 = nguyenLy1.khoang_cach_neo_vach_A1
	bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1 = nguyenLy1.khoang_cach_neo_vach_A1
	bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1 = nguyenLy1.khoang_cach_neo_vach_A1
	bpy.data.scenes[nguyenLy].SoLuongNeoVach_NL1 = round((3.14 * bpy.data.scenes[nguyenLy].ChieuRong2a_NL1 / 2) / (nguyenLy1.khoang_cach_neo_vach_A1), 0) + 1
	bpy.data.scenes[nguyenLy].MatDoNeoHong_Sh_NL1 = nguyenLy1.mat_do_neo_hong_Sh
	bpy.data.scenes[nguyenLy].KhoangCachNeoHong_A2_NL1 = nguyenLy1.khoang_cach_neo_hong_A2'''
	
	'''EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "MatDoNeoVach_Sn_NL1", CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "KhoangCachNeoVachTheoChuVi_NL1", CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "KhoangCachNeoVachTheoTruc_NL1", CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], "ChieuDai1ThanhNeoNoc_Ln_NL1", CompareLocation, CompareLocationCallback, True))
			
			# neo hông
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], 'ChieuDai1ThanhNeoHong_Lh_NL1', CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], 'KhoangCachNeoHong_A2_NL1', CompareLocation, CompareLocationCallback, True))
			EventWatcher.AddWatcher(EventWatcher(bpy.data.scenes[nguyenLy], 'MatDoNeoHong_Sh_NL1', CompareLocation, CompareLocationCallback, True))'''
	 # CongTrinhNgam
	 
	# Quy đổi đơn vị tính
	Rk = Rk * 1000000
	u_s_k_d_d_v = u_s_k_d_d_v * 1000000
	u_s_n_d_d_v = u_s_n_d_d_v * 1000000
	
	h 		= c_s_H  # Chiều sâu hầm lò
	H1 		= c_c_H1  # Chiều cao đường lò
		
	a 		= c_r_2a / 2  # Nửa chiều rộng đường lò
		
	# Hệ số đẩy ngang
	if l_d_d == 'RAN':				# Đất: RẮN
		hs_day_ngang = h_s_P / (1 - h_s_P)
	else:							#Đất : YẾU
		hs_day_ngang = tan(radians(45 - g_m_s_t / 2)) ** 2

	## Tính Chiều cao vòm sụt lở : cot(radians(45 + g_m_s_t/2)) = tan(radians(45 - g_m_s_t/2))
	b 		= (a + H1 * cot(radians(45 + g_m_s_t / 2))) / f  																# (4.3)			OK
	##### END
	
	## Khả năng chịu lực của thanh Neo: Pc																					(4.10)
	Fc 		= (Dn / 2)**2 * math.pi																							# Tính diện tích thanh cốt neo, (m2) - OK
	Klv 	= Dlv  # Hệ số làm việc của thanh neo
	
	#Pc 		= (Fc * Rk * Klv)  # Khả năng chịu lực của thanh Neo														(1) - CHANGE
	Pc 		= (Fc * Rk * Klv) / 10000  # Khả năng chịu lực của thanh Neo													(1) - OK		(T)
	##### END
	
	## Khả năng chịu lực của thanh Neo với đk với điều kiện dính bám của cốt Neo với bê Tông: Pcb	(4.11)
	Klvz 	= Dlvz  # Hệ số về điều kiện làm việc của khóa neo
	
	#Pcb 	= math.pi * Dn * T1 * Lz * Kz * Klvz  # Khả năng chịu lực của thanh Neo											(2)				CHANGE
	Pcb 	= (math.pi * Dn * 1000000 * T1 * Lz * Kz * Klvz) / 10000  # Khả năng chịu lực của thanh Neo						(2)				(T)
	#print("Pcb", Pcb)
	##### END

	## Khả năng chịu lực của thanh Neo với đk với điều kiện dính bám của Đất đá với bê Tông: Pcb	(4.12)
	#Pbd 	= math.pi * Dlk * T2 * Lz * Kz * Klvz  # Khả năng chịu lực của thanh Neo										(3)				CHANGE
	Pbd 	= (math.pi * Dlk * 1000000 * T2 * Lz * Kz * Klvz) / 10000  # Khả năng chịu lực của thanh Neo					(3)
	#print("Pbd", Pbd)
	##### END
	
	# Lấy min của (1) & (2) (3)
	Pn 		= min([Pc, Pcb, Pbd])  # 4	Khả năng chịu lực 1 thanh neo	Pn	MN
	# print("Pn", Pn)
	
	# NEO NOC
	if type == 'n':
		print('Xu ly Neo noc')
		## Tính Chiều dài toàn bộ thanh Neo nóc
		Ln 		= b + 1.5 * Lz + Lk																								#(4.4)			OK
		Lz = (Ln - b - Lk)/1.5
		##### END
		
		## Mật độ Neo S Nóc(vách): Sn
		Qv 		= round(b, 2) * round(Y, 2)
		S 		= (Qv * round(Np, 2)) / round(Pn, 2)																			#(4.5)			OK
		##### END
		
		## Hệ số ổn định của đất đá vách
		Nv 		= (round(u_s_k_d_d_v, 2) * round(Kc, 2) * hs_l_b) / (round(K2, 2) * hs_day_ngang * round(Y, 2) * 10000 * h)		# (4.1) 			OK
		##### END
		
		
		# Sn: Mật độ neo vách
		if field == 'Sn':
			#print("S", field)
			S 			= bpy.data.scenes[nguyenLy].MatDoNeoVach_Sn_NL1
			
			## Tính khoảng cách giữa các Neo Nóc lò
			a1 		= (1 / S) ** 0.5																								#(4.6)			OK
			##### END
			
			# Out: Khoảng cách neo vach: theo chu vi - trục
			bpy.data.scenes[nguyenLy].KhoangCachNeoVach_A1_NL1 			= a1
			bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1 	= a1
			bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1 	= a1
						
			# Out: Hệ số an toàn nóc lò
			Np 		= S * Pn / Qv
			bpy.data.scenes[nguyenLy].HeSoAnToanNocLo_Np_NL1 = Np
			
			# Out: Số lượng neo hông
			bpy.data.scenes[nguyenLy].SoLuongNeoVach_NL1 = round((3.14 * c_r_2a / 2) / (a1), 0) + 1
		
		# Ln: Chiều dài thanh neo nóc
		elif field == 'Ln':
			#print("Ln", field)
			Ln 			= bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoNoc_Ln_NL1
			S 			= bpy.data.scenes[nguyenLy].MatDoNeoVach_Sn_NL1
			
			# Tính lại Lz
			Lz = (Ln - b - Lk) / 1.5
			if Lz < 0.4:
				Kz = 0.58
			else:
				Kz = 0.55
			
			Pcb 	= (math.pi * Dn * 1000000 * T1 * Lz * Kz * Klvz) / 10000  # Khả năng chịu lực của thanh Neo						(2)				(T)

			
			Pbd 	= (math.pi * Dlk * 1000000 * T2 * Lz * Kz * Klvz) / 10000  # Khả năng chịu lực của thanh Neo					(3)
			
			# Lấy min của (1) & (2) (3)
			Pn 		= min([Pc, Pcb, Pbd])  # 4	Khả năng chịu lực 1 thanh neo	Pn	MN
			
			# Out: Khả năng chịu lực 1 thanh neo
			bpy.data.scenes[nguyenLy].ChieuDaiKhoaNeo_Lz_NL1 = Lz
			
			# Out: Hệ số điều chỉnh chiều dài khóa neo Kz
			bpy.data.scenes[nguyenLy].HeSoDieuChinhChieuDaiKhoaNeo_Kz_NL1 = Kz
			
			# Out: Khả năng chịu lực 1 thanh neo
			bpy.data.scenes[nguyenLy].KhaNangChiuLuc1ThanhNeo_Pn_NL1 = Pn
			# Out: S
			#S 		= (Qv * round(Np, 2)) / round(Pn, 2)																			#(4.5)			OK
			
			# Out: Hệ số an toàn nóc lò
			Np 		= S * Pn / Qv
			bpy.data.scenes[nguyenLy].HeSoAnToanNocLo_Np_NL1 = Np
			
		# cv: Khoảng cách neo vách theo chu vi
		elif field == 'cv':
			print("CV", field)
			theo_chuvi 	= bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1
			theo_truc 	= bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1
			
			# Out: Mật độ neo vách
			S 			= 1 / (theo_chuvi * theo_truc)
			bpy.data.scenes[nguyenLy].MatDoNeoVach_Sn_NL1 = S
			
			# Out: Hệ số an toàn nóc lò
			Np 		= S * Pn / Qv
			bpy.data.scenes[nguyenLy].HeSoAnToanNocLo_Np_NL1 = Np
		
		# t: Khoảng cách neo vách theo trục
		elif field == 't':
			print("t", field)
			theo_chuvi 	= bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1
			theo_truc 	= bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1
			
			# Out: Mật độ neo vách
			S 			= 1 / (theo_chuvi * theo_truc)
			bpy.data.scenes[nguyenLy].MatDoNeoVach_Sn_NL1 = S
			
			# Out: Hệ số an toàn nóc lò
			Np 		= S * Pn / Qv
			bpy.data.scenes[nguyenLy].HeSoAnToanNocLo_Np_NL1 = Np
			
		'''elif field == 'A1':			# Khoảng cách neo vách
			print("A1", field)
			a1 			= bpy.data.scenes[nguyenLy].KhoangCachNeoVach_A1_NL1
			
			# Out: Mật độ neo vách
			S 			= 1 / a1**2
			bpy.data.scenes[nguyenLy].MatDoNeoVach_Sn_NL1 = S
			
			# Out: Khoảng cách neo vach: theo chu vi - trục
			bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoChuVi_NL1 = a1
			bpy.data.scenes[nguyenLy].KhoangCachNeoVachTheoTruc_NL1 = a1
			
			# Out: Hệ số an toàn nóc lò
			Np 		= S * Pn / Qv
			bpy.data.scenes[nguyenLy].HeSoAnToanNocLo_Np_NL1 = Np'''
		# Out: Chieu dai thanh neo noc
		#bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoNoc_Ln_NL1 = Ln
		
		
	# NEO HONG
	elif type == 'h':
		print('Xu ly Neo hong')
		## Hệ số ổn định của đất đá Neo hông
		Nh 		= (round(u_s_n_d_d_v, 2) * round(Kc, 2) * hs_l_b) / (round(K1, 2) * round(Y, 2) * 10000 * h)					# (4.2)
		##### END
		
		## Tính Chiều dài toàn bộ thanh neo ở hông lò
		g_m_s_t = np.degrees(np.arctan(f))
		C 		= H1 * cot(radians(45 + g_m_s_t / 2))																			#(4.8) Bán kính chiều rộng lò được mở rộng do đất đá trượt
		'''print("C", C)
		print(Nh)'''
		Lh 		= (C / Nh) + Lz + Lk																							#(4.7)
		# Lh 		= C + 1.5 * Lz + Lk
		##### END

		## Mật độ Neo Hông
		Qh 		= (round(b, 2) + H1) * round(Y, 2) * hs_day_ngang 																# Tải trọng hông lò (MPa)
		Sh 		= (Qh * round(Nph, 2)) / round(Pn, 2)																			# (4.9)
		##### END

		## Tính khoảng cách giữa các Neo Hông
		a2 		= (1 / Sh) ** 0.5																								# (4.6) Tương tự a1
		##### END 
		
		# Sh: Mật độ neo hông
		if field == 'Sh':
			Sh 		= bpy.data.scenes[nguyenLy].MatDoNeoHong_Sh_NL1
			
			## Tính khoảng cách giữa các Neo Hông
			a2 		= (1 / Sh) ** 0.5																							# (4.6) Tương tự a1
			##### END 
			
			# OUT: Khoảng cách neo hông
			bpy.data.scenes[nguyenLy].KhoangCachNeoHong_A2_NL1 = a2
			
			# Out: Số lượng neo hông
			bpy.data.scenes[nguyenLy].SoLuongNeoHong_NL1 = round((3.14 * c_r_2a / 2) / (a2), 0) + 1
		
		# Lh: Chiều dài 1 thanh neo hông
		elif field == 'Lh':
			Lh 		= bpy.data.scenes[nguyenLy].ChieuDai1ThanhNeoHong_Lh_NL1
		
		# A2: Khoảng cách neo hông
		elif field == 'A2':
			a2 		= bpy.data.scenes[nguyenLy].KhoangCachNeoHong_A2_NL1
		
	'''self.he_so_on_dinh_dat_da_vach_Nv 			= Nv	# 1		Hệ số ổn định đất đá vách	nv	-
	self.he_so_on_dinh_dat_da_hong_Nh 			= Nh	# 2		Hệ số ổn định đất đá hông	nh	-
	self.chieu_cao_vom_sup_lo_B 				= b		# 3		Chiều cao vòm sụp lở	b	m
	self.kha_nang_chiu_luc_1_thanh_neo_Pn 		= Pn	# 4		Khả năng chịu lực 1 thanh neo	Pn	MN
	self.chieu_dai_1_thanh_neo_noc_Ln 			= Ln	# 5		Chiều dài 1 thanh neo nóc	Ln	m
	self.chieu_dai_1_thanh_neo_hong_Lh 			= Lh	# 6		Chiều dài 1 thanh neo hông	Lh	m
	self.mat_do_neo_vach_Sn 					= S		# 7		Mật độ neo vách	Sn	neo/m2
	self.khoang_cach_neo_vach_A1 				= a1	# 8		Khoảng cách neo vách	a1	m
	self.mat_do_neo_hong_Sh 					= Sh	# 9		Mật độ neo hông	Sh	neo/m2
	self.khoang_cach_neo_hong_A2 				= a2	# 10	Khoảng cách neo hông	a2	m'''

'''def reportHeSoOnDinh(type):
	nguyenLy 	= bpy.context.screen.scene.name
	
	if type 	== 'Nv':
		Nv = bpy.data.scenes[nguyenLy].HeSoOnDinhDatDaVach_Nv_NL1
		if Nv >= 4:
			print("Nv >= 4")
			#self.report({'INFO'}, "Mouse coords are %d %d" % (self.x, self.y))
	elif type 	== 'Nh':
		Nh = bpy.data.scenes[nguyenLy].HeSoOnDinhDatDaHong_Nh_NL1'''

# The callback to execute when the cursor's location changes
def CompareLocationCallback(watcher, newValue, fieldName):
	#print(bpy.context.screen.scene.name[0])
	if bpy.context.screen.scene.name[0] == '1':
		#print('124')
		if fieldName == 'MatDoNeoVach_Sn_NL1':
			updateKetQuaDauRa('n', 'Sn')
		elif fieldName == 'ChieuDai1ThanhNeoNoc_Ln_NL1':
			updateKetQuaDauRa('n', 'Ln')
		# elif fieldName == 'KhoangCachNeoVachTheoChuVi_NL1':
			# updateKetQuaDauRa('n', 'cv')
		# elif fieldName == 'KhoangCachNeoVach_A1_NL1':
			# updateKetQuaDauRa('n', 'A1')
		# elif fieldName == 'KhoangCachNeoVachTheoTruc_NL1':
			# updateKetQuaDauRa('n', 't')
		elif fieldName == 'MatDoNeoHong_Sh_NL1':
			updateKetQuaDauRa('h', 'Sh')
		# elif fieldName == 'ChieuDai1ThanhNeoHong_Lh_NL1':
			# updateKetQuaDauRa('h', 'Lh')
		# elif fieldName == 'KhoangCachNeoHong_A2_NL1':
			# updateKetQuaDauRa('A2')
		# elif fieldName == 'HeSoOnDinhDatDaVach_Nv_NL1':
			# reportHeSoOnDinh('Nv')
		# elif fieldName == 'HeSoOnDinhDatDaHong_Nh_NL1':
			# reportHeSoOnDinh('Nh')
		# else:
			# changeEvent_NL1()
		
	elif bpy.context.screen.scene.name[0] == '3':
		calculator(1)
	# print( 'New value', newValue )


# excute
# bpy.app.handlers.scene_update_post.append(cb_scene_update)
# Install the watcher which will run the callback
# EventWatcher.AddWatcher( EventWatcher( bpy.data.scenes[0], "cursor_location", CompareLocation, CompareLocationCallback, True ) )
###########################################################



class RegisterParameter(bpy.types.PropertyGroup):
	### NGUYEN LY 1 ###
	# TO DO
	# -NEO
	duong_kinh_thep_neo_Dn_NL1 								= 0.02				# 1	Đường kính thép neo	dn	m
	kha_nang_chiu_keo_thep_neo_Rk_NL1 						= 270.0				# 2	Khả năng chịu kéo thép neo	Rn	MPa					210.0
	duong_kinh_lo_khoan_Dlk_NL1 							= 0.042				# 3	Đường kính lỗ khoan	dlk	m # 	0.04 - 0.03
	luc_dinh_ket_giua_be_tong_va_thanh_neo_T1_NL1 			= 6.4				# 4	Lực dính kết giữa bê tông và thanh neo	1	MPa	50.0 - 7.9
	luc_dinh_ket_giua_be_tong_va_dat_da_T2_NL1 				= 2.0				# 5	Lực dính kết giữa bê tông và đất đá	2	MPa		40.0 - 4.5
	dieu_kien_lo_khoan_NL1 									= 'khô/ẩm'  		# 6	Điều kiện lỗ khoan	Khô/ẩm	
	he_so_lam_viec_cua_neo_Dlv_NL1 							= 0.9				# 7	Hệ số làm việc của neo 	dlv						0.9 - 0.8
	he_so_lam_viec_cua_khoa_neo_Dlvz_NL1 					= 0.6				# 8	Hệ số làm việc của khóa neo 	dlvz			0.8
	# he_so_tap_trung_ung_suat_keo_K2_NL1					= 0.5				#9	Hệ số tập trung ứng suất kéo 	k2	
	# he_so_tap_trung_ung_suat_K1_NL1						= 2.0				#10	Hệ số tập trung ứng suất	k1	-
	chieu_dai_neo_nho_ra_mat_lo_Lk_NL1 						= 0.2				# 11	Chiều dài neo nhô ra mặt lộ	Lk				0.06
	he_so_qua_tai_noc_lo_Np_NL1 							= 1.2				# 12	Hệ số quá tải nóc lò	np					1.6
	he_so_qua_tai_hong_lo_Nph_NL1 							= 1.2				# 13	Hệ số quá tải hông lò	nph	-
	he_so_dieu_chinh_chieu_dai_khoa_neo_Kz_NL1 				= 0.55				# 14	Hệ số điều chỉnh chiều dài khóa neo 	kz	0.55
	chieu_dai_khoa_neo_Lz_NL1 								= 0.4				# Chiều dài khóa neo 	Lz	0.4 - 0.3
	he_so_an_toan_noc_lo_Np_NL1 							= 1.2
	he_so_an_toan_hong_lo_Nph_NL1 							= 1.2

	bpy.types.Scene.DuongKinhThepNeo_Dn_NL1 				= FloatProperty(name="Đường kính thép neo", default=duong_kinh_thep_neo_Dn_NL1, min=0.0)
	bpy.types.Scene.ThepNhom_NL1 							= EnumProperty(name="Thép Nhóm", items=arrThepNhom)
	bpy.types.Scene.KhaNangChiuKeoThepNeo_Rk_NL1 			= FloatProperty(name="Khả năng chịu kéo thép neo", default=kha_nang_chiu_keo_thep_neo_Rk_NL1)
	bpy.types.Scene.DuongKinhLoKhoan_Dlk_NL1 				= FloatProperty(name="Đường kính lỗ khoan", default=duong_kinh_lo_khoan_Dlk_NL1, min=0.0)
	bpy.types.Scene.LucDinhKetGiuaBeTongVaThanhNeo_T1_NL1 	= FloatProperty(name="Lực dính kết giữa bê tông và thanh neo", default=luc_dinh_ket_giua_be_tong_va_thanh_neo_T1_NL1, min=0.0)
	bpy.types.Scene.LucDinhKetGiuaBeTongVaDatDa_T2_NL1 		= FloatProperty(name="Lực dính kết giữa bê tông và đất đá", default=luc_dinh_ket_giua_be_tong_va_dat_da_T2_NL1, min=0.0)
	bpy.types.Scene.DieuKienLoKhoan_Dlv_NL1 				= EnumProperty(name="Điều kiện lỗ khoan", items=arrDieuKienLoKhoan)  # default = dieu_kien_lo_khoan_NL1,
	bpy.types.Scene.HeSoLamViecCuaNeo_Dlv_NL1 				= FloatProperty(name="Hệ số làm việc của neo", default=he_so_lam_viec_cua_neo_Dlv_NL1, min=0.9, max=1.0)
	bpy.types.Scene.HeSoLamViecCuaKhoaNeo_Dlvz_NL1 			= FloatProperty(name="Hệ số làm việc của khóa neo", default=he_so_lam_viec_cua_khoa_neo_Dlvz_NL1, min=0.6, max=0.9)
	# bpy.types.Scene.HeSoTapTrungUngSuatKeo_K2_NL1			= FloatProperty(name = "Hệ số tập trung ứng suất kéo k2", default = he_so_tap_trung_ung_suat_keo_K2_NL1, min = 0.23, max = 1.0)
	# bpy.types.Scene.HeSoTapTrungUngSuat_K1_NL1				= FloatProperty(name = "Hệ số tập trung ứng suất k1", default = he_so_tap_trung_ung_suat_K1_NL1)
	bpy.types.Scene.ChieuDaiNeoNhoRaMatLo_Lk_NL1 			= FloatProperty(name="Chiều dài neo nhô ra mặt lộ", default=chieu_dai_neo_nho_ra_mat_lo_Lk_NL1, min=0.0)
	bpy.types.Scene.HeSoQuaTaiNocLo_Np_NL1 					= FloatProperty(name="Hệ số quá tải nóc lò", default=he_so_qua_tai_noc_lo_Np_NL1, min=0.0)
	bpy.types.Scene.HeSoQuaTaiHongLo_Nph_NL1 				= FloatProperty(name="Hệ số quá tải hông lò", default=he_so_qua_tai_hong_lo_Nph_NL1, min=0.0)
	bpy.types.Scene.HeSoDieuChinhChieuDaiKhoaNeo_Kz_NL1 	= FloatProperty(name="Hệ số điều chỉnh chiều dài khóa neo", default=he_so_dieu_chinh_chieu_dai_khoa_neo_Kz_NL1, min=0.0)
	bpy.types.Scene.ChieuDaiKhoaNeo_Lz_NL1 					= FloatProperty(name="Chiều dài khóa neo", default=chieu_dai_khoa_neo_Lz_NL1, min=0.3)			#, max=0.4
	bpy.types.Scene.HeSoAnToanNocLo_Np_NL1 					= FloatProperty(name="Hệ số an toàn nóc lò", default= he_so_an_toan_noc_lo_Np_NL1, min=0.0)
	bpy.types.Scene.HeSoAnToanHongLo_Nph_NL1 				= FloatProperty(name="Hệ số an toàn hông lò", default= he_so_an_toan_hong_lo_Nph_NL1, min=0.0)

	# -DATDA
	trong_luong_the_tich_NL1 								= 2.63			# 1	Trọng lượng thể tích		T/m3	2.6 - 2.74
	ung_suat_keo_dat_da_NL1 								= 3.56			# 2	Ứng suất kéo đất đá vách	k	T/m2	781.0 - 54.7
	ung_suat_nen_dat_dat_vach_NL1 							= 53.0			# 3	Ứng suất nén đất đá vách	n	T/m2	1910.0 - 133.77
	goc_ma_sat_trong_NL1 									= 31.0			# 4	Góc ma sát trong		Độ		30- 32
	he_so_Poisson_NL1 										= 0.21			# 5	Hệ số Poisson					0.7
	loai_dat_da_NL1 										= 'Rắn/Yếu'		# 6	Loại đất đá	Rắn/Yếu	-
	he_so_luu_bien_NL1 										= 0.7			# 7	Hệ số lưu biến		- (Rắn:0.7-1.0) - (Yếu:05-0.7)	0.8
	he_so_tap_trung_ung_suat_keo_K2_NL1 					= 0.3			# 8	Hệ số tập trung ứng suất kéo	k2					0.5 - 0.27
	he_so_tap_trung_ung_suat_K1_NL1 						= 2.0			# 9	Hệ số tập trung ứng suất	k1
	chieu_day_phan_lop_trung_binh_B_NL1 					= 1.6			# 10	Chiều dày phân lớp trung bình	b	m
	he_so_giam_yeu_cau_truc_Kc_NL1 							= 0.2			# Hệ số giảm yếu cấu trúc Kc							0.6 - 0.4
	he_so_kien_co_trung_binh_dat_da_f_NL1 					= 4.0			# Hệ số kiên cố trung bình của đất đá F					5.0

	bpy.types.Scene.TrongLuongTheTich_NL1 					= FloatProperty(name="Trọng lượng thể tích", default=trong_luong_the_tich_NL1, min=0.0)
	bpy.types.Scene.UngSuatKeoDatDaVach_NL1 				= FloatProperty(name="Ứng suất kéo đất đá vách", default=ung_suat_keo_dat_da_NL1, min=0.0)
	bpy.types.Scene.UngSuatNenDatDaVach_NL1 				= FloatProperty(name="Ứng suất nén đất đá vách", default=ung_suat_nen_dat_dat_vach_NL1, min=0.0)
	bpy.types.Scene.GocMaSatTrong_NL1 						= FloatProperty(name="Góc ma sát trong", default=goc_ma_sat_trong_NL1)
	bpy.types.Scene.HoSoPoisson_NL1 						= FloatProperty(name="Hệ số Poisson", default=he_so_Poisson_NL1)
	bpy.types.Scene.LoaiDatDa_NL1 							= EnumProperty(name="Loại đất đá", items=arrLoaiDatDa)  # , default = loai_dat_da_NL1
	bpy.types.Scene.HeSoLuuBien_NL1 						= FloatProperty(name="Hệ số lưu biến", default=he_so_luu_bien_NL1, min=0.5, max=1.0)
	bpy.types.Scene.HeSoTapTrungUngSuatKeo_K2_NL1 			= FloatProperty(name="Hệ số tập trung ứng suất kéo", default=he_so_tap_trung_ung_suat_keo_K2_NL1, min=0.23, max=1.0)
	bpy.types.Scene.HeSoTapTrungUngSuat_K1_NL1 				= FloatProperty(name="Hệ số tập trung ứng suất", default=he_so_tap_trung_ung_suat_K1_NL1, min=0.0)
	bpy.types.Scene.ChieuDayPhanLopTrungBinhB_NL1 			= FloatProperty(name="Chiều dày phân lớp trung bình", default=chieu_day_phan_lop_trung_binh_B_NL1, min=0.0)
	bpy.types.Scene.HeSoGiamYeuCauTrucKc_NL1 				= FloatProperty(name="Hệ số giảm yếu cấu trúc", default=he_so_giam_yeu_cau_truc_Kc_NL1, min=0.0)
	bpy.types.Scene.HeSoKienCoTBDatDa_f_NL1 				= FloatProperty(name="Hệ số kiên cố trung bình của đất đá", default=he_so_kien_co_trung_binh_dat_da_f_NL1, min=0.0)

	# -Cong trinh ngam
	chieu_sau_H_NL1 										= 100.0 	# 1	Chiều sâu 	H	m			120.0
	chieu_rong_2a_NL1 										= 5.0 		# 2	Chiều rộng 	2a	m				3.0 - 4.9 - 3.2
	chieu_cao_H1_NL1 										= 3.68 		# 3	Chiều cao	h1	m				2.0 - 3.5 - 2.6
	chieu_cao_tuong_lo_H2_NL1 								= 1.0 		# 4	Chiều cao tường lò	h2	m		
	chieu_dai_NL1 											= 10.0 		# 5	Chiều cao dài	m		

	bpy.types.Scene.ChieuSauH_NL1 							= FloatProperty(name="Chiều sâu", default=chieu_sau_H_NL1, min=0.0)
	bpy.types.Scene.ChieuRong2a_NL1 						= FloatProperty(name="Chiều rộng", default=chieu_rong_2a_NL1, min=0.0)
	bpy.types.Scene.ChieuCaoH1_NL1 							= FloatProperty(name="Chiều cao", default=chieu_cao_H1_NL1, min=0.0)
	bpy.types.Scene.ChieuCaoTuongLoH2_NL1 					= FloatProperty(name="Chiều cao tường", default=chieu_cao_tuong_lo_H2_NL1, min=0.0)
	bpy.types.Scene.ChieuDai_NL1 							= FloatProperty(name="Chiều dài", default=chieu_dai_NL1, min=0.0)
 
	# Đầu ra Nguyên Lý 1
	he_so_on_dinh_dat_da_vach_Nv_NL1 						= 0.0  # 10.81		#1	Hệ số ổn định đất đá vách	nv	-
	he_so_on_dinh_dat_da_hong_Nh_NL1 						= 0.0  # 2.20		#2	Hệ số ổn định đất đá hông	nh	-
	chieu_cao_vom_sup_lo_B_NL1 								= 0.0  # 0.43		#3	Chiều cao vòm sụp lở	b	m
	kha_nang_chiu_luc_1_thanh_neo_Pn_NL1 					= 0.0  # 0.88		#4	Khả năng chịu lực 1 thanh neo	Pn	MN
	chieu_dai_1_thanh_neo_noc_Ln_NL1 						= 0.0  # 1.43		#5	Chiều dài 1 thanh neo nóc	Ln	m
	chieu_dai_1_thanh_neo_hong_Lh_NL1 						= 0.0  # 0.82		#6	Chiều dài 1 thanh neo hông	Lh	m
	mat_do_neo_vach_Sn_NL1 									= 0.0  # 1.50		#7	Mật độ neo vách	Sn	neo/m2
	khoang_cach_neo_vach_A1_NL1 							= 0.0  # 0.82		#8	Khoảng cách neo vách	a1	m
	so_luong_neo_vach_NL1 									= 0  				#8	Số lượng neo vách
	mat_do_neo_hong_Sh_NL1 									= 0.0  # 1.15		#9	Mật độ neo hông	Sh	neo/m2
	khoang_cach_neo_hong_A2_NL1 							= 0.0  # 0.93		#10	Khoảng cách neo hông	a2	m
	so_luong_neo_hong_NL1 									= 0  				#11	Số lượng neo hông

	bpy.types.Scene.HeSoOnDinhDatDaVach_Nv_NL1 				= FloatProperty(name="Hệ số ổn định đất đá vách", default=he_so_on_dinh_dat_da_vach_Nv_NL1)
	bpy.types.Scene.HeSoOnDinhDatDaHong_Nh_NL1 				= FloatProperty(name="Hệ số ổn định đất đá hông", default=he_so_on_dinh_dat_da_hong_Nh_NL1)
	bpy.types.Scene.ChieuCaoVomSupLo_B_NL1 					= FloatProperty(name="Chiều cao vòm sụp lở", default=chieu_cao_vom_sup_lo_B_NL1)
	bpy.types.Scene.KhaNangChiuLuc1ThanhNeo_Pn_NL1 			= FloatProperty(name="Khả năng chịu lực 1 thanh neo", default=kha_nang_chiu_luc_1_thanh_neo_Pn_NL1)
	bpy.types.Scene.ChieuDai1ThanhNeoNoc_Ln_NL1 			= FloatProperty(name="Chiều dài 1 thanh neo nóc", default=chieu_dai_1_thanh_neo_noc_Ln_NL1)
	bpy.types.Scene.ChieuDai1ThanhNeoHong_Lh_NL1 			= FloatProperty(name="Chiều dài 1 thanh neo hông", default=chieu_dai_1_thanh_neo_hong_Lh_NL1)
	bpy.types.Scene.MatDoNeoVach_Sn_NL1 					= FloatProperty(name="Mật độ neo vách", default=mat_do_neo_vach_Sn_NL1)
	bpy.types.Scene.KhoangCachNeoVach_A1_NL1 				= FloatProperty(name="Khoảng cách neo vách", default=khoang_cach_neo_vach_A1_NL1)
	bpy.types.Scene.KhoangCachNeoVachTheoChuVi_NL1 			= FloatProperty(name="- Theo chu vi", default=0.0)
	bpy.types.Scene.KhoangCachNeoVachTheoTruc_NL1 			= FloatProperty(name="- Theo trục", default=0.0)
	bpy.types.Scene.SoLuongNeoVach_NL1 						= IntProperty(name="Số lượng", default=so_luong_neo_vach_NL1)
	
	bpy.types.Scene.MatDoNeoHong_Sh_NL1 					= FloatProperty(name="Mật độ neo hông", default=mat_do_neo_hong_Sh_NL1)
	bpy.types.Scene.KhoangCachNeoHong_A2_NL1 				= FloatProperty(name="Khoảng cách neo hông", default=khoang_cach_neo_hong_A2_NL1)
	bpy.types.Scene.SoLuongNeoHong_NL1 						= IntProperty(name="Số lượng", default=so_luong_neo_hong_NL1)
	
	bpy.types.Scene.ThongBaoNv 								= StringProperty(name="", default="")
	bpy.types.Scene.ThongBaoNh 								= StringProperty(name="", default="")
	###### END NGUYEN LY 1 #####
	##########################################################################################

	### NGUYEN LY 2 ###
	# TO DO
	'''S = 1
	a = 0.5
	Y = 2.7
	A = S * S
	R = 1
	g_m_s_t = radians(35)
	k = 1
	L = 3
	c = 10
	D = 4
	r = 2'''

	# -NEO
	khoang_cach_giua_cac_neo_S_NL2 								= 1.0	# 1		Khoảng cách giữa các Neo												1.0
	he_so_phu_thuoc_vao_thoi_gian_lap_dat_neo_a_NL2 			= 0.5	# 2		Hệ số phụ thuộc vào thời gian lắp đặt Neo								1.0
	dien_tich_vung_gia_tai_1_thanh_neo_A_NL2 					= khoang_cach_giua_cac_neo_S_NL2**2	# 3		Diện tích vùng gia tải của 1 thanh neo (S x S)							1.0
	chieu_dai_cua_neo_L_NL2 									= 3.0	# 4		Chiều dài của Neo														4.0
	ban_kinh_chiu_cat_cua_dv_dat_da_duoc_gia_co_NL2 			= 0.25	# 5		Bán kính chịu cắt của Đơn vị Đất Đá được gia cố							4.0

	# -DATDA
	trong_luong_rieng_của_dam_da_mang_tai_Y_NL2 				= 27	# 6		Trọng lượng riêng của dầm đá mang tải									2.7
	goc_ma_sat_trong_NL2 										= 32.0	# 7		Góc ma sát trong														35.0
	ty_so_giua_ap_luc_ngang_tb_va_thang_dung_tb_k_NL2 			= 0.6	# 8		Tỷ số giữa áp lục ngang trung bình và áp lực thằng đứng trung bình		1.0
	luc_ket_dinh_giua_cac_lop_dat_da_c_NL2 						= 50.0	# 9		Lực kết dính giữa các lớp đất đá										10.0
	chieu_cao_vung_dat_da_khong_gay_ung_suat_D_NL2 				= 4.0	# 10	Chiều cao vùng đất đá không gây ứng suất								3.0
	#ban_kinh_r_NL2 											= 2.0	# 11																			2.0

	# - Công trình ngầm
	chieu_rong_cong_trinh_NL2 									= 3.0	# 12	Chiều rộng công trình
	chieu_cao_cong_trinh_NL2 									= 4.0	# 13	Chiều cao công trình
	
	bpy.types.Scene.KhoangCachGiuaCacNeo_S_NL2 					= FloatProperty(name="Khoảng cách giữa các Neo", default=khoang_cach_giua_cac_neo_S_NL2, min=0.0)
	bpy.types.Scene.HeSoPhuThuocThoiGianLapDatNeo_NL2 			= FloatProperty(name="Hệ số phụ thuộc vào thời gian lắp đặt Neo", default=he_so_phu_thuoc_vao_thoi_gian_lap_dat_neo_a_NL2, min=0.0, max=1.0)
	bpy.types.Scene.DienTichVungGiaTai1ThanhNeo_A_NL2 			= FloatProperty(name="Diện tích vùng gia tải của 1 thanh neo", default=dien_tich_vung_gia_tai_1_thanh_neo_A_NL2, min=0.0)
	bpy.types.Scene.ChieuDaiCuaNeo_L_NL2 						= FloatProperty(name="Chiều dài của Neo", default=chieu_dai_cua_neo_L_NL2, min=0.0)
	bpy.types.Scene.BankinhChiuCatCuaDVDatDaDuocGiaCo_NL2 		= FloatProperty(name="Bán kính chịu cắt của Đơn vị Đất Đá được gia cố", default=ban_kinh_chiu_cat_cua_dv_dat_da_duoc_gia_co_NL2, min=0.0)

	bpy.types.Scene.TrongLuongRiengCuaDamDaMangTai_NL2 			= FloatProperty(name="Trọng lượng riêng của dầm đá mang tải", default=trong_luong_rieng_của_dam_da_mang_tai_Y_NL2, min=0.0)
	bpy.types.Scene.GocMaSatTrong_NL2 							= FloatProperty(name="Góc ma sát trong", default=goc_ma_sat_trong_NL2)
	bpy.types.Scene.TySoGiuaApLucNgangVaThangDungTB_K_NL2 		= FloatProperty(name="Tỷ số giữa áp lục ngang trung bình và áp lực thằng đứng trung bình", default=ty_so_giua_ap_luc_ngang_tb_va_thang_dung_tb_k_NL2)
	bpy.types.Scene.LucKetDinhGiuaCacLopDatDa_c_NL2 			= FloatProperty(name="Lực kết dính giữa các lớp đất đá", default=luc_ket_dinh_giua_cac_lop_dat_da_c_NL2)
	bpy.types.Scene.ChieuCaoVungDatDaKhongGayUngSuat_D_NL2 		= FloatProperty(name="Chiều cao vùng đất đá không gây ứng suất", default=chieu_cao_vung_dat_da_khong_gay_ung_suat_D_NL2, min=0.0)
	#bpy.types.Scene.BanKinh_r_NL2 								= FloatProperty(name="Bán kính", default=ban_kinh_r_NL2)
	
	bpy.types.Scene.ChieuRongCongTrinh_NL2 						= FloatProperty(name="Chiều rộng công trình", default=chieu_rong_cong_trinh_NL2, min=0.0)
	bpy.types.Scene.ChieuCaoCongTrinh_NL2 						= FloatProperty(name="Chiều cao công trình", default=chieu_cao_cong_trinh_NL2, min=0.0)
	
	# - Đầu ra: Lực kéo neo đơn vị T
	bpy.types.Scene.LucKeoNeoDonVi_T_NL2 						= FloatProperty(name="Lực kéo neo đơn vị", default=0.0)
	###### END NGUYEN LY 2 #####

	##########################################################################################

	### NGUYEN LY 3 ###
	# -NEO
	duong_kinh_kheo_neo_Db_NL3 				= 0.02
	modul_dan_hoi_thep_neo_Eb_NL3 			= 296.8263
	modul_dan_hoi_vua_xi_mang_Eg_NL3 		= 54.5982
	duong_kinh_lo_khoan_Dh_NL3 				= 0.036
	chieu_dai_neo_L_NL3 					= 1.5
	khoang_cach_neo_A_NL3 					= 0.8

	# -DATDA
	trong_luong_the_tich_NL3 				= 2.6
	modul_dan_hoi_da_Er_NL3 				= 48.7678
	he_so_Poisson_NL3 						= 0.7

	# -Cong trinh ngam
	chieu_sau_CTN_NL3 						= 160.0
	ban_kinh_CTN_NL3 						= 3.0

	# Bán kinh đầu vào(tích điểm)
	out_ban_kinh_NL3 						= 1.02

	# -Sau
	ung_suat_phap_tuyen_sau_NL3 			= 356.95
	ung_suat_tiep_tuyen_sau_NL3 			= 475.52
	bien_dang_sau_NL3 						= 1.82
	chuyen_vi_sau_NL3 						= 130.43
	modul_dan_hoi_sau_NL3 					= 48.77

	# -Truoc
	ung_suat_phap_tuyen_truoc_NL3 			= 161.18
	ung_suat_tiep_tuyen_truoc_NL3 			= 789.42
	bien_dang_truoc_NL3 					= 2.5
	chuyen_vi_truoc_NL3 					= 163.17
	modul_dan_hoi_truoc_NL3 				= 48.77

	###END Set Default Value
	bpy.types.Scene.DuongKinhThepNeoDb_NL3 		= FloatProperty(name="Đường kính thép Neo",
														   default=duong_kinh_kheo_neo_Db_NL3)
	bpy.types.Scene.ModulDanHoiThepNeoEb_NL3 	= FloatProperty(name="Modul đàn hồi thép Neo",
															 default=modul_dan_hoi_thep_neo_Eb_NL3)
	bpy.types.Scene.ModulDanHoiVuaXiMangEg_NL3 	= FloatProperty(name="Modul đàn hồi vữa xi măng",
															   default=modul_dan_hoi_vua_xi_mang_Eg_NL3)
	bpy.types.Scene.DuongKinhLoKhoanDh_NL3 		= FloatProperty(name="Đường kinh lỗ khoan",
														   default=duong_kinh_lo_khoan_Dh_NL3)
	bpy.types.Scene.ChieuDaiNeoL_NL3 			= FloatProperty(name="Chiều dài Neo", default=chieu_dai_neo_L_NL3)
	bpy.types.Scene.KhoangCachNeoA_NL3 			= FloatProperty(name="Khoảng cách Neo", default=khoang_cach_neo_A_NL3)
	# END NEO

	# DATDA
	bpy.types.Scene.TrongLuongTheTich_NL3 		= FloatProperty(name="Trọng lượng thể tích", default=trong_luong_the_tich_NL3)
	bpy.types.Scene.ModulDanHoiDaEr_NL3 		= FloatProperty(name="Modul đàn hồi đá", default=modul_dan_hoi_da_Er_NL3)
	bpy.types.Scene.HeSoPoisson_NL3 			= FloatProperty(name="Hệ số Poisson", default=he_so_Poisson_NL3)
	##END DATDA

	# Cong Trinh Ngam
	bpy.types.Scene.ChieuSauCTN_NL3 			= FloatProperty(name="Chiều sâu CTN", default=chieu_sau_CTN_NL3)
	bpy.types.Scene.BanKinhCTN_NL3 				= FloatProperty(name="Bán kính CTN", default=ban_kinh_CTN_NL3)
	##END Cong Trinh Ngam

	# Result
	bpy.types.Scene.ChonLoai 					= EnumProperty(items=arrChonLoai, name="Đồ thị")  # , default = 0 -> lỗi set default
	bpy.types.Scene.OutBanKinh_NL3 				= FloatProperty(name="Bán kính", default=out_ban_kinh_NL3)

	# Sau
	bpy.types.Scene.UngSuatPhapTuyenSau_NL3 	= FloatProperty(name='', default=ung_suat_phap_tuyen_sau_NL3)
	bpy.types.Scene.UngSuatTiepTuyenSau_NL3 	= FloatProperty(name='', default=ung_suat_tiep_tuyen_sau_NL3)
	bpy.types.Scene.BienDangSau_NL3 			= FloatProperty(name='', default=bien_dang_sau_NL3)
	bpy.types.Scene.ChuyenViSau_NL3 			= FloatProperty(name='', default=chuyen_vi_sau_NL3)
	bpy.types.Scene.ModulDanHoiSau_NL3 			= FloatProperty(name='', default=modul_dan_hoi_sau_NL3)

	# Trước
	bpy.types.Scene.UngSuatPhapTuyenTruoc_NL3 	= FloatProperty(name='', default=ung_suat_phap_tuyen_truoc_NL3)
	bpy.types.Scene.UngSuatTiepTuyenTruoc_NL3 	= FloatProperty(name='', default=ung_suat_tiep_tuyen_truoc_NL3)
	bpy.types.Scene.BienDangTruoc_NL3 			= FloatProperty(name='', default=bien_dang_truoc_NL3)
	bpy.types.Scene.ChuyenViTruoc_NL3 			= FloatProperty(name='', default=chuyen_vi_truoc_NL3)
	bpy.types.Scene.ModulDanHoiTruoc_NL3 		= FloatProperty(name='', default=modul_dan_hoi_truoc_NL3)
	##END Result
	###### END NGUYEN LY 3 #####

	##########################################################################################

	### NGUYEN LY 4 ###
	# NEO
	kha_nang_chiu_luc_1_thanh_neo_NL4 					= 10.0  # 0.88		#4	Khả năng chịu lực 1 thanh neo	Pn	MN
	chieu_dai_1_thanh_neo_Ln_NL4 						= 0.0  # 1.43			#5	Chiều dài 1 thanh neo nóc	Ln	m
	so_luong_neo_giu_khoi_nem_NL4 						= 1  # 0.82			# Số lượng Neo giữ khối Nêm
	## END NEO

	bpy.types.Scene.KhaNangChiuLuc1ThanhNeo_NL4 		= FloatProperty(name='Khả năng chịu lực 1 thanh neo', default=kha_nang_chiu_luc_1_thanh_neo_NL4, min=0.0)
	bpy.types.Scene.ChieuDai1ThanhNeo_NL4 				= FloatProperty(name='Chiều dài 1 thanh neo', default=chieu_dai_1_thanh_neo_Ln_NL4, min=0.0)
	bpy.types.Scene.SoLuongNeoGiuKhoiNem_NL4 			= IntProperty(name='Số lượng Neo giữ khối Nêm', default=so_luong_neo_giu_khoi_nem_NL4, min=0)

	# Default Khe nứt 1
	goc_doc_1_NL4 									= 51.0  # Góc dốc									45
	goc_phuong_vi_1_NL4 							= 138.0  # Góc phương vị của khe nứt				180
	ten_khe_nut_1_NL4 								= 'Khe nứt 1'  # Tên khe nứt

	# Default Khe nứt 2
	goc_doc_2_NL4 									= 40.0  # Góc dốc									45
	goc_phuong_vi_2_NL4 							= 355.0  # Góc phương vị của khe nứt					60
	ten_khe_nut_2_NL4 								= 'Khe nứt 2'  # Tên khe nứt

	# Default Khe nứt 3
	goc_doc_3_NL4 									= 67.0  # Góc dốc									45
	goc_phuong_vi_3_NL4 							= 219.0  # Góc phương vị của khe nứt				300
	ten_khe_nut_3_NL4 								= 'Khe nứt 3'  # Tên khe nứt

	# Default góc phương vị của Công trình ngầm
	goc_doc__cong_trinh_ngam_NL4 					= 0  # Góc dốc của Công trình ngầm
	goc_phuong_vi__cong_trinh_ngam_NL4 				= 45.0  # Góc phương vị của Công trình ngầm
	chieu_rong_cong_trinh_ngam_NL4 					= 10.0  # Góc dốc của Công trình ngầm					4
	trong_luong_the_tich_dat_da_NL4 				= 2.7  # Trọng lượng thể tích của đất đá T/m3

	# Default thể tích khối NÊM

	the_tich_khoi_nem_noc_NL4 						= 0.0  # Thể tích của Khối Nêm nóc
	trong_luong_khoi_nem_noc_NL4 					= 0.0  # Trọng lượng của thể tích khối Nêm nóc
	he_so_an_toan_khoi_nem_noc_NL4 					= 0.0  # Trọng lượng của thể tích khối Nêm nóc

	bpy.types.Scene.GocDoc_1_NL4 					= FloatProperty(name='Góc dốc 1', default=goc_doc_1_NL4)
	bpy.types.Scene.GocPhuongVi_1_NL4 				= FloatProperty(name='Góc phương vị 1', default=goc_phuong_vi_1_NL4)
	bpy.types.Scene.TenKheNut_1_NL4 				= StringProperty(name='Tên khe nứt 1', default=ten_khe_nut_1_NL4)

	bpy.types.Scene.GocDoc_2_NL4 					= FloatProperty(name='Góc dốc 2', default=goc_doc_2_NL4)
	bpy.types.Scene.GocPhuongVi_2_NL4 				= FloatProperty(name='Góc phương vị 2', default=goc_phuong_vi_2_NL4)
	bpy.types.Scene.TenKheNut_2_NL4 				= StringProperty(name='Tên khe nứt 2', default=ten_khe_nut_2_NL4)

	bpy.types.Scene.GocDoc_3_NL4 					= FloatProperty(name='Góc dốc 3', default=goc_doc_3_NL4)
	bpy.types.Scene.GocPhuongVi_3_NL4 				= FloatProperty(name='Góc phương vị 3', default=goc_phuong_vi_3_NL4)
	bpy.types.Scene.TenKheNut_3_NL4 				= StringProperty(name='Tên khe nứt 3', default=ten_khe_nut_3_NL4)
	bpy.types.Scene.TrongLuongTheTichDatDa_NL4 		= FloatProperty(name='Trọng lượng thể tích của đất đá', default=trong_luong_the_tich_dat_da_NL4)

	bpy.types.Scene.GocDoc_CongTrinhNgam_NL4 		= FloatProperty(name='Góc dốc', default=goc_doc__cong_trinh_ngam_NL4)
	bpy.types.Scene.GocPhuongVi_CongTrinhNgam_NL4 	= FloatProperty(name='Góc phương vị', default=goc_phuong_vi__cong_trinh_ngam_NL4)
	bpy.types.Scene.ChieuRong_CongTrinhNgam_NL4 	= FloatProperty(name='Chiều rộng', default=chieu_rong_cong_trinh_ngam_NL4)

	# Thể tích khối NÊM
	bpy.types.Scene.TheTich_KhoiNem_Noc_NL4 		= FloatProperty(name='Thể tích khối NÊM nóc', default=the_tich_khoi_nem_noc_NL4)
	bpy.types.Scene.TrongLuong_KhoiNem_Noc_NL4 		= FloatProperty(name='Trọng lượng khối NÊM nóc', default=trong_luong_khoi_nem_noc_NL4)
	bpy.types.Scene.HeSo_AnToan_KhoiNem_Noc_NL4 	= FloatProperty(name='Hệ số an toàn khối NÊM nóc', default=he_so_an_toan_khoi_nem_noc_NL4)
	###### END NGUYEN LY 4 #####

	##########################################################################################

	### NGUYEN LY 5 ###
	# TO DO
	# NEO
	duong_kinh_theo_neo_db_NL5 							= 0.0254  # 1	Đường kính thép neo	db	m
	duong_kinh_lo_khoan_Dh_NL5 							= 0.036  # 2	Đường kính lỗ khoan	dh	m
	modul_dan_hoi_thep_neo_Eb_NL5 						= 210.0  # 3	Modul đàn hồi thép neo	Eb	MPa
	# modul_dan_hoi_vua_neo_NL5							= 0.0			 #4	Modul đàn hồi vữa xi măng 	Eg	MPa
	modul_dan_hoi_truot_vua_neo_NL5 					= 0.0  # 4	Modul đàn hồi truowngt vữa neo 	Gg	MPa
	chieu_dai_neo_L_NL5 								= 2.0  # 5	Chiều dài neo	L	m
	khoang_cach_neo_A_NL5 								= 1.2  # 6	Khoảng cách neo	a	m
	# he_so_Poisson_neo_NL5								= 0.35			 #7	Hệ số Poisson neo	b	-
	# he_so_Poisson_vua_neo_NL5							= 0.35			 #8	Hệ số Poisson vữa neo	g	-


	bpy.types.Scene.DuongKinhThepNeoDb_NL5 				= FloatProperty(name='Đường kính thép neo',
														   default=duong_kinh_theo_neo_db_NL5)
	bpy.types.Scene.DuongKinhLoKhoanDh_NL5 				= FloatProperty(name='Đường kính lỗ khoan',
														   default=duong_kinh_lo_khoan_Dh_NL5)
	bpy.types.Scene.ModulDanHoiThepNeoEb_NL5 			= FloatProperty(name='Modul đàn hồi thép neo',
															 default=modul_dan_hoi_thep_neo_Eb_NL5)
	# bpy.types.Scene.ModulDanHoiVuaNeo_Eg_NL5			= FloatProperty(name='Modul đàn hồi vữa xi măng Eg', default = modul_dan_hoi_vua_neo_NL5)
	bpy.types.Scene.ChieuDaiNeoL_NL5 					= FloatProperty(name='Chiều dài neo', default=chieu_dai_neo_L_NL5, min=1.0, max = 10.0)
	bpy.types.Scene.KhoangCachNeoA_NL5 					= FloatProperty(name='Khoảng cách neo', default=khoang_cach_neo_A_NL5)
	# bpy.types.Scene.HeSoPoissonNeo_NL5					= FloatProperty(name='Hệ số Poisson neo', default = he_so_Poisson_neo_NL5)
	# bpy.types.Scene.HeSoPoissonVuaNeo_NL5				= FloatProperty(name='Hệ số Poisson vữa neo', default = he_so_Poisson_vua_neo_NL5)
	bpy.types.Scene.ModulDanHoiTruotVuaNeo_Gg_NL5 		= FloatProperty(name='Modul đàn hồi trượt vữa neo',
																  default=modul_dan_hoi_truot_vua_neo_NL5)

	# Đất Đá
	do_ben_nen_don_truc_NL5 			= 0.5	# 1	Độ bền nén đơn trục	c	MPa
	modul_dan_hoi_Em_NL5 				= 0.5	# 2	Modul đàn hồi	Er(Em)	GPa
	modul_dan_hoi_truot_Gm_NL5 			= 0.5	# Modul đàn hồi trượt	Gm	GPa
	he_so_Poisson_NL5 					= 0.35	# 3	Hệ số Poisson		-
	ap_luc_nuoc_ngam_Po_NL5 			= 1.0	# 4	Áp lực nước ngầm	Po	MPa

	bpy.types.Scene.DoBenNenDonTruc_NL5 			= FloatProperty(name='Độ bền nén đơn trục', default=do_ben_nen_don_truc_NL5)
	bpy.types.Scene.ModulDanHoi_Em_NL5 				= FloatProperty(name='Modul đàn hồi', default=modul_dan_hoi_Em_NL5)
	bpy.types.Scene.ModulDanHoiTruot_Gm_NL5 		= FloatProperty(name='Modul đàn hồi trượt của khối đá', default=modul_dan_hoi_truot_Gm_NL5)
	bpy.types.Scene.HeSoPoisson_NL5 				= FloatProperty(name='Hệ số Poisson', default=he_so_Poisson_NL5)
	bpy.types.Scene.ApLucNuocNgamPo_NL5 			= FloatProperty(name='Áp lực nước ngầm', default=ap_luc_nuoc_ngam_Po_NL5)

	# Công Trình Ngầm
	ban_kinh_Ra_NL5 					= 4.75  # 1	Bán kính 	Ra	m

	bpy.types.Scene.BanKinhRa_NL5 						= FloatProperty(name='Bán kính Ra', default=ban_kinh_Ra_NL5, min=0.0)

	# Đầu ra
	bpy.types.Scene.BanKinhVungDanHoi_Re_NL5 			= FloatProperty(name='Bán kính vùng đàn hồi', default=0.0, min=0.0)
	bpy.types.Scene.BanKinhVungDeo_Rf_NL5 				= FloatProperty(name='Bán kính vùng dẻo', default=0.0, min=0.0)
	# Đầu ra

	###### END NGUYEN LY 5 #####

	# NEO
	
##END Result

def register():
	# bpy.utils.register_module(__name__)
	bpy.utils.register_class(RegisterParameter)
	
	bpy.utils.register_class(ToolPanel_NEO)
	bpy.utils.register_class(ToolPanel_DATDA)
	bpy.utils.register_class(ToolPanel_CongTrinhNgam)
	bpy.utils.register_class(initOutPut)
	
	#bpy.utils.register_class(KetQuaTinh)
	bpy.utils.register_class(KetQuaTinh_NguyenLy_1)
	bpy.utils.register_class(KetQuaTinh_NguyenLy_2)
	bpy.utils.register_class(KetQuaTinh_NguyenLy_3)
	bpy.utils.register_class(KetQuaTinh_NguyenLy_4)
	bpy.utils.register_class(KetQuaTinh_NguyenLy_5)
	
	bpy.utils.register_class(dothi_NguyenLy_1)
	bpy.utils.register_class(cap_nhat_dothi_NguyenLy_1)
	bpy.utils.register_class(dothi_NguyenLy_2)
	bpy.utils.register_class(dothi_NguyenLy_3)


def unregister():
	# bpy.utils.unregister_module(__name__)
	bpy.utils.unregister_class(RegisterParameter)
	
	bpy.utils.unregister_class(ToolPanel_NEO)
	bpy.utils.unregister_class(ToolPanel_DATDA)
	bpy.utils.unregister_class(ToolPanel_CongTrinhNgam)
	
	bpy.utils.unregister_class(initOutPut)
	
	#bpy.utils.unregister_class(KetQuaTinh)
	bpy.utils.unregister_class(KetQuaTinh_NguyenLy_1)
	bpy.utils.unregister_class(KetQuaTinh_NguyenLy_2)
	bpy.utils.unregister_class(KetQuaTinh_NguyenLy_3)
	bpy.utils.unregister_class(KetQuaTinh_NguyenLy_4)
	bpy.utils.unregister_class(KetQuaTinh_NguyenLy_5)
	
	bpy.utils.unregister_class(dothi_NguyenLy_1)
	bpy.utils.unregister_class(cap_nhat_dothi_NguyenLy_1)
	bpy.utils.unregister_class(dothi_NguyenLy_2)
	bpy.utils.unregister_class(dothi_NguyenLy_3)


#    return
if __name__ == "__main__":
	register()


# Nguyên lý 1 : Nguyên lý Treo
class NguyenLy1:
	def __init__(self, Dn, Rk, Dlk, T1, T2, Dlv, Dlvz, Lk, Np, Nph, Kz, Lz,  # Neo
				 Y, u_s_k_d_d_v, u_s_n_d_d_v, g_m_s_t, h_s_P, l_d_d, hs_l_b, K2, K1, cd_pl_tb_B, Kc, f,  # DatDa
				 c_s_H, c_r_2a, c_c_H1, c_c_t_l_H2,  # CongTrinhNgam
				 ):
		# Quy đổi đơn vị tính
		Rk = Rk * 1000000
		u_s_k_d_d_v = u_s_k_d_d_v * 1000000
		u_s_n_d_d_v = u_s_n_d_d_v * 1000000
		
		#print("Math.atan", np.degrees(np.arctan(4)))
		# NEO
		self.duong_kinh_thep_neo_Dn 								= Dn			# 1		Đường kính thép neo						dn	m
		self.kha_nang_chiu_keo_thep_neo_Rk 							= Rk			# 2		Khả năng chịu kéo thép neo				Rn	MPa
		self.duong_kinh_lo_khoan_Dlk 								= Dlk			# 3		Đường kính lỗ khoan	dlk	m #
		self.luc_dinh_ket_giua_be_tong_va_thanh_neo_T1 				= T1			# 4		Lực dính kết giữa bê tông và thanh neo	1	MPa #
		self.luc_dinh_ket_giua_be_tong_va_dat_da_T2 				= T2			# 5		Lực dính kết giữa bê tông và đất đá		2	MPa
		# self.dieu_kien_lo_khoan									= 'khô/ẩm'		# 6		Điều kiện lỗ khoan						Khô/ẩm	-
		self.he_so_lam_viec_cua_neo_Dlv 							= Dlv 			# 7		Hệ số làm việc của neo 					dlv	-
		self.he_so_lam_viec_cua_khoa_neo_Dlvz 						= Dlvz			# 8		Hệ số làm việc của khóa neo 			dlvz	-
		self.he_so_tap_trung_ung_suat_keo_K2 						= K2			# 9		Hệ số tập trung ứng suất kéo 			k2	-
		self.he_so_tap_trung_ung_suat_K1 							= K1			# 10	Hệ số tập trung ứng suất				k1	-
		self.chieu_dai_neo_nho_ra_mat_lo_Lk 						= Lk			# 11	Chiều dài neo nhô ra mặt lộ				Lk	-
		self.he_so_qua_tai_noc_lo_Np 								= Np			# 12	Hệ số quá tải nóc lò					np	-
		self.he_so_qua_tai_hong_lo_Nph 								= Nph			# 13	Hệ số quá tải hông lò					nph	-
		self.he_so_dieu_chinh_chieu_dai_khoa_neo_Kz 				= Kz			# 14	Hệ số điều chỉnh chiều dài khóa neo 	kz	-
		self.chieu_dai_khoa_neo_Lz									= Lz			# 		Chiều dài khóa neo 						Lz	-

		# -DATDA
		self.trong_luong_the_tich 									= Y				# 1		Trọng lượng thể tích		T/m3
		self.ung_suat_keo_dat_da 									= u_s_k_d_d_v	# 2		Ứng suất kéo đất đá vách	k	T/m2
		self.ung_suat_nen_dat_dat_vach 								= u_s_n_d_d_v	# 3		Ứng suất nén đất đá vách	n	T/m2
		self.goc_ma_sat_trong 										= g_m_s_t		# 4		Góc ma sát trong		Độ
		self.he_so_Poisson 											= h_s_P			# 5		Hệ số Poisson		-
		self.loai_dat_da 											= l_d_d			# 6		Loại đất đá	Rắn/Yếu	-
		self.he_so_luu_bien 										= hs_l_b		# 7		Hệ số lưu biến		-
		self.he_so_tap_trung_ung_suat_keo_K2 						= K2			# 8		Hệ số tập trung ứng suất kéo	k2	-
		self.he_so_tap_trung_ung_suat_K1 							= K1			# 9		Hệ số tập trung ứng suất	k1	-
		self.chieu_day_phan_lop_trung_binh_B 						= cd_pl_tb_B	# 10	Chiều dày phân lớp trung bình	b	m
		self.he_so_giam_yeu_cau_truc_Kc 							= Kc			# 		Hệ số giảm yếu cấu trúc Kc
	
		# -Cong trinh ngam
		self.chieu_sau_H 					= c_s_H			# 1	Chiều sâu 	H	m
		self.chieu_rong_2a 					= c_r_2a		# 2	Chiều rộng 	2a	m
		self.chieu_cao_H1 					= c_c_H1		# 3	Chiều cao	h1	m
		self.chieu_cao_tuong_lo_H2 			= c_c_t_l_H2	# 4	Chiều cao tường lò	h2	m

		h 		= c_s_H  # Chiều sâu hầm lò
		H1 		= c_c_H1  # Chiều cao đường lò

		a 		= c_r_2a / 2  # Nửa chiều rộng đường lò
		
		# Hệ số đẩy ngang
		if l_d_d == 'RAN':				# Đất: RẮN
			hs_day_ngang = h_s_P / (1 - h_s_P)
		else:							#Đất : YẾU
			hs_day_ngang = tan(radians(45 - g_m_s_t / 2)) ** 2

		'''hs_day_ngang = 0.307
		H1 = 3.5
		a = 2.45
		u_s_k_d_d_v = 54.7
		Kc = 0.4
		K2 = 0.27
		Y = 2.74
		h = 200
		hs_l_b = 0.7
		g_m_s_t = 32
		Dn = 0.02
		T1 = 7.9
		T2 = 4.5
		Lz = 0.4
		Kz = 0.55
		Klvz = 0.6
		Rk = 270000000
		Klv = 0.8
		Klv = 0.8
		Fc = 0.00031
		f = 5
		'''
		## Hệ số ổn định của đất đá vách
		#Nv 		= (u_s_k_d_d_v * Kc * hs_l_b) / (K2 * hs_day_ngang * Y * h)													# (4.1) 		CHANGE
		#hs_l_b = 0.5
		Nv 		= (round(u_s_k_d_d_v, 2) * round(Kc, 2) * hs_l_b) / (round(K2, 2) * hs_day_ngang * round(Y, 2) * 10000 * h)		# (4.1) 			OK
		##### END

		## Hệ số ổn định của đất đá Neo hông
		#hs_l_b = 0.7
		print("u_s_n_d_d_v", u_s_n_d_d_v)
		print("K1", K1)
		# Nh 		= (u_s_n_d_d_v * Kc * hs_l_b) / (K1 * hs_day_ngang * Y * h)		# (4.2)
		Nh 		= (round(u_s_n_d_d_v, 2) * round(Kc, 2) * hs_l_b) / (round(K1, 2) * round(Y, 2) * 10000 * h)					# (4.2)
		##### END

		# Nv = 3.37
		## Tính Chiều cao vòm sụt lở : cot(radians(45 + g_m_s_t/2)) = tan(radians(45 - g_m_s_t/2))
		b 		= (a + H1 * cot(radians(45 + g_m_s_t / 2))) / f  																# (4.3)			OK
		##### END

		# b = 0.88
		
		## Khả năng chịu lực của thanh Neo: Pc																					(4.10)
		Fc 		= (Dn / 2)**2 * math.pi																							# Tính diện tích thanh cốt neo, (m2) - OK
		Klv 	= Dlv  # Hệ số làm việc của thanh neo
		
		#Pc 		= (Fc * Rk * Klv)  # Khả năng chịu lực của thanh Neo														(1) - CHANGE
		Pc 		= (Fc * Rk * Klv) / 10000  # Khả năng chịu lực của thanh Neo													(1) - OK		(T)
		
		##### END
		## Khả năng chịu lực của thanh Neo với đk với điều kiện dính bám của cốt Neo với bê Tông: Pcb	(4.11)
		Klvz 	= Dlvz  # Hệ số về điều kiện làm việc của khóa neo
		
		#Pcb 	= math.pi * Dn * T1 * Lz * Kz * Klvz  # Khả năng chịu lực của thanh Neo											(2)				CHANGE
		Pcb 	= (math.pi * Dn * 1000000 * T1 * Lz * Kz * Klvz) / 10000  # Khả năng chịu lực của thanh Neo						(2)				(T)
		#print("Pcb", Pcb)
		##### END

		## Khả năng chịu lực của thanh Neo với đk với điều kiện dính bám của Đất đá với bê Tông: Pcb	(4.12)
		#Pbd 	= math.pi * Dlk * T2 * Lz * Kz * Klvz  # Khả năng chịu lực của thanh Neo										(3)				CHANGE
		Pbd 	= (math.pi * Dlk * 1000000 * T2 * Lz * Kz * Klvz) / 10000  # Khả năng chịu lực của thanh Neo					(3)
		#print("Pbd", Pbd)
		##### END
		 
		# Lấy min của (1) & (2) (3)
		Pn 		= min([Pc, Pcb, Pbd])  # 4	Khả năng chịu lực 1 thanh neo	Pn	MN
		# print("Pn", Pn)
		## Tính Chiều dài toàn bộ thanh Neo nóc
		Ln 		= b + 1.5 * Lz + Lk																								#(4.4)			OK
		##### END

		## Mật độ Neo S Nóc(vách)
		Qv 		= round(b, 2) * round(Y, 2)
		#print("Qv", Qv)
		print("Np", Np)
		print("Pn", Pn)
		S 		= (Qv * round(Np, 2)) / round(Pn, 2)																			#(4.5)			OK
		#print("S", S)
		##### END

		## Tính khoảng cách giữa các Neo Nóc lò
		a1 		= (1 / S) ** 0.5																								#(4.6)			OK
		##### END

		## Tính Chiều dài toàn bộ thanh neo ở hông lò
		'''print("1.5 * Lz + Lk", 1.5 * Lz + Lk)
		print("b", b)
		print("H1", H1)
		print("g_m_s_t", g_m_s_t)
		print("tan(radians(90 - g_m_s_t / 2))", tan(radians(45 - g_m_s_t / 2)))
		print("cot(radians(45 + g_m_s_t / 2))", cot(radians(45 + g_m_s_t / 2)))'''
		g_m_s_t = np.degrees(np.arctan(f))
		C 		= H1 * cot(radians(45 + g_m_s_t / 2))																			#(4.8) Bán kính chiều rộng lò được mở rộng do đất đá trượt
		'''print("C", C)
		print(Nh)'''
		Lh 		= (C / Nh) + Lz + Lk																							#(4.7)
		# Lh 		= C + 1.5 * Lz + Lk
		##### END

		## Mật độ Neo Hông
		Qh 		= (round(b, 2) + H1) * round(Y, 2) * hs_day_ngang 																# Tải trọng hông lò (MPa)
		Sh 		= (Qh * round(Nph, 2)) / round(Pn, 2)																			# (4.9)
		##### END

		## Tính khoảng cách giữa các Neo Hông
		a2 		= (1 / Sh) ** 0.5																								# (4.6) Tương tự a1
		##### END

		self.he_so_on_dinh_dat_da_vach_Nv 			= Nv	# 1		Hệ số ổn định đất đá vách	nv	-
		self.he_so_on_dinh_dat_da_hong_Nh 			= Nh	# 2		Hệ số ổn định đất đá hông	nh	-
		self.chieu_cao_vom_sup_lo_B 				= b		# 3		Chiều cao vòm sụp lở	b	m
		self.kha_nang_chiu_luc_1_thanh_neo_Pn 		= Pn	# 4		Khả năng chịu lực 1 thanh neo	Pn	MN
		self.chieu_dai_1_thanh_neo_noc_Ln 			= Ln	# 5		Chiều dài 1 thanh neo nóc	Ln	m
		self.chieu_dai_1_thanh_neo_hong_Lh 			= Lh	# 6		Chiều dài 1 thanh neo hông	Lh	m
		self.mat_do_neo_vach_Sn 					= S		# 7		Mật độ neo vách	Sn	neo/m2
		self.khoang_cach_neo_vach_A1 				= a1	# 8		Khoảng cách neo vách	a1	m
		self.mat_do_neo_hong_Sh 					= Sh	# 9		Mật độ neo hông	Sh	neo/m2
		self.khoang_cach_neo_hong_A2 				= a2	# 10	Khoảng cách neo hông	a2	m

# Nguyên lý 3 : Nguyên lý Gia Cố
class nguyenlygiaco(object):
	# Khoi tao cac bien tuong tac voi nguoi dung
	def __init__(self, 	d_tltt 		= 1, 
						d_hs_ps 	= 2,
				 # d_usp0=3, d_usp1=4, d_ust0=5, d_ust1=1, d_bd0=1, d_bd1=1, d_cv0=1, d_cv1=1, d_E1=1,
						d_E0 		= 1,
						ct_H 		= 20,
						ct_R 		= 3,
						n_L 		= 3,
						n_db		= 1,
						n_dh 		= 1,
						n_a 		= 9,
						n_Eb 		= 7,
 						n_Eg 		= 1,
						r 			= 1):
		# Các biến dùng chung
		self.r 			= r
		
		# Dau vao dat da
		self.d_tltt 	= d_tltt
		self.d_hs_ps 	= d_hs_ps
		
		# Dau ra dat da
		# self.d_usp0	= d_usp0
		# self.d_usp1	= d_usp1
		# self.d_ust0	= d_ust0
		# self.d_ust1	= d_ust1
		# self.d_bd0	= d_bd0
		# self.d_bd1	= d_bd1
		# self.d_cv0	= d_cv0
		# self.d_cv1	= d_cv1
		self.d_E0 		= d_E0
		# self.d_E1		=d_E1
		
		# Dau vao cong trinh
		self.ct_H 		= ct_H
		self.ct_R 		= ct_R
		
		# Dau vao neo
		self.n_L 		= n_L
		self.n_db 		= n_db
		self.n_dh 		= n_dh
		self.n_a 		= n_a
		self.n_Eb 		= n_Eb
		self.n_Eg 		= n_Eg

	# Tinh he so A
	def hs_A(self):
		n_dh 	= self.n_dh
		n_db 	= self.n_db
		n_Eg 	= self.n_Eg
		n_Eb 	= self.n_Eb
		n_a 	= self.n_a
		d_E0 	= self.d_E0
		ct_R 	= self.ct_R
		# Cong thuc 5.2 trang 2 -tac gia Cong
		kq 		= (math.pi / 4) * ((n_dh ** 2 * (n_Eg - d_E0) + (n_db ** 2) * (n_Eb - n_Eg)) / (n_a ** 2 * d_E0)) * (ct_R ** 2)
		
		return kq

	# Tinh he so D
	def hs_D(self):
		a 		= self.ct_R
		b 		= a + self.n_L
		hs_A 	= self.hs_A()
		# Cong thuc 5.3 trang 2 -tac gia Cong
		kq 		= (3 * hs_A) / (2 * (b ** 4)) - (3 * hs_A) / (2 * (a ** 4)) - (1 / (a ** 2))
		
		return kq

	# Modul đàn hồi Sau khi Neo
	def E1(self, bk):
		E0 		= self.d_E0
		hs_A 	= self.hs_A()
		r 		= bk  # self.r
		R 		= self.ct_R
		
		if r >= R:
			# Cong thuc 5.1 trang 2 -tac gia Cong
			kq 	= E0 * (1 + hs_A / (r ** 2))
		else:
			kq 	= 0
			
		return kq

	'''def dothi_E(self):
		max 	= self.ct_R * 6
		bk 		= self.r
		self.r 	= np.arange(0, max, 0.1)
		y 		= self.E1(bk)

		plt.plot(self.r, y)
		plt.show()'''

	# Đồ thị ứng suất pháp : Trước - Sau
	def dothi_ungsuatphap(self):
		max = self.ct_R * 6

		self.r = np.arange(self.ct_R + 0.1, max, 0.1)

		# Hiện thị tiêu đề trên thanh Taskbar window
		fig1 = plt.figure()
		fig1.canvas.set_window_title('Phần mềm tính toán Neo - TKV. Nguyên lý gia cố')

		# Ứng suất pháp tuyến trước khi Neo
		pFunc = np.vectorize(self.ungsuatphap0)  # To do
		y = pFunc(self.r)
		line1, = plt.plot(self.r, y, label="Trước neo", color="blue", linestyle='--')
		plt.plot(self.r, y)

		# Ứng suất pháp tuyến sau khi Neo
		self.r = np.arange(self.ct_R + 0.1, max, 0.1)
		pFunc = np.vectorize(self.ungsuatphap1)
		y1 = pFunc(self.r)
		line2, = plt.plot(self.r, y1, label="Sau neo", color="red")
		plt.plot(self.r, y1)

		plt.legend(handles=[line1, line2], loc = 4)
		plt.xlabel('Bán kính r')
		plt.ylabel('Ứng suất pháp tuyến')
		plt.title('Biến thiên của ứng suất pháp tuyến theo bán kính r')

		plt.show()

	# Đồ thị ứng suất tiếp tuyến : Trước - Sau
	def dothi_ungsuattiep(self):
		max = self.ct_R * 6

		# Hiện thị tiêu đề trên thanh Taskbar window
		fig1 = plt.figure()
		fig1.canvas.set_window_title('Phần mềm tính toán Neo - TKV. Nguyên lý gia cố')

		self.r = np.arange(self.ct_R + 0.1, max, 0.1)

		# Ứng suất tiếp tuyến trước khi Neo
		pFunc = np.vectorize(self.ungsuattiep0)
		y = pFunc(self.r)
		line1, = plt.plot(self.r, y, color="blue", label="Trước neo", linestyle='--')

		# Ứng suất tiếp tuyến Sau khi Neo
		pFunc = np.vectorize(self.ungsuattiep1)
		y1 = pFunc(self.r)
		line2, = plt.plot(self.r, y1, label="Sau neo", color="red")
		# Create another legend for the second line.

		plt.legend(handles=[line1, line2], loc = 4)
		# plt.legend((y[0], y1[0]), ('Trước khi Neo', 'Sau khi Neo'))

		plt.xlabel('Bán kính r')
		plt.ylabel('Ứng suất tiếp tuyến')
		plt.title('Biến thiên của ứng suất tiếp tuyến theo bán kính r')

		plt.show()

	# Đồ thị chuyển vị : Trước - Sau
	def dothi_chuyenvi(self):
		max = self.ct_R * 6

		# Hiện thị tiêu đề trên thanh Taskbar window
		fig1 = plt.figure()
		fig1.canvas.set_window_title('Phần mềm tính toán Neo - TKV. Nguyên lý gia cố')

		self.r = np.arange(self.ct_R + 0.1, max, 0.1)

		# Chuyển vị trước khi Neo
		pFunc = np.vectorize(self.chuyenvi0)
		y = pFunc(self.r)
		line1, = plt.plot(self.r, y, color="blue", label="Trước neo", linestyle='--')

		# Chuyển vị Sau khi Neo
		pFunc = np.vectorize(self.chuyenvi1)
		y1 = pFunc(self.r)
		line2, = plt.plot(self.r, y1, label="Sau neo", color="red")
		# Create another legend for the second line.

		plt.legend(handles=[line1, line2], loc = 4)

		plt.xlabel('Bán kính r')
		plt.ylabel('Chuyển vị')
		plt.title('Biến thiên của chuyển vị theo bán kính r')

		plt.show()

	# Đồ thị biến dạng : Trước - Sau
	def dothi_biendang(self):
		max = self.ct_R * 6

		# Hiện thị tiêu đề trên thanh Taskbar window
		fig1 = plt.figure()
		fig1.canvas.set_window_title('Phần mềm tính toán Neo - TKV. Nguyên lý gia cố')

		self.r = np.arange(self.ct_R + 0.1, max, 0.1)

		# Chuyển vị trước khi Neo
		pFunc = np.vectorize(self.biendang0)
		y = pFunc(self.r)
		line1, = plt.plot(self.r, y, color="blue", label="Trước neo", linestyle='--')

		# Chuyển vị Sau khi Neo
		pFunc = np.vectorize(self.biendang1)
		y1 = pFunc(self.r)
		line2, = plt.plot(self.r, y1, label="Sau neo", color="red")
		# Create another legend for the second line.

		plt.legend(handles=[line1, line2], loc = 4)

		plt.xlabel('Bán kính r')
		plt.ylabel('Biến dạng')
		plt.title('Biến thiên của biến dạng theo bán kính r')

		plt.show()

	# Đồ thị Modul đàn hồi 1 : Trước - Sau
	def dothi_moduldanhoi(self):
		max = self.ct_R * 6

		# Hiện thị tiêu đề trên thanh Taskbar window
		fig1 = plt.figure()
		fig1.canvas.set_window_title('Phần mềm tính toán Neo - TKV. Nguyên lý gia cố')

		self.r = np.arange(self.ct_R + 0.1, max, 0.1)

		# Chuyển vị trước khi Neo
		pFunc = np.vectorize(self.E1)
		y = self.d_E0 + self.r - self.r
		line1, = plt.plot(self.r, y, color="blue", label="Trước neo", linestyle='--')

		# Chuyển vị Sau khi Neo
		pFunc = np.vectorize(self.E1)
		y1 = pFunc(self.r)
		line2, = plt.plot(self.r, y1, label="Sau neo", color="red")
		# Create another legend for the second line.

		plt.legend(handles=[line1, line2], loc = 4)
		# plt.legend(handles=[line2], loc=4)

		plt.xlabel('Bán kính r')
		plt.ylabel('Modul đàn hồi')
		plt.title('Biến thiên của Modul đàn hồi theo bán kính r')

		plt.show()

	# Ứng suất pháp tuyến TRƯỚC khi Neo
	def ungsuatphap0(self, bk):  # To do
		r = bk  # self.r
		R = self.ct_R
		if r >= R:
			P = self.d_tltt * self.ct_H
			# CT trang 77 -tac gia Phich. Ung suat tiep truoc khi neo
			kq = P * (1 - (R / r) ** 2)
		else:
			kq = 0

		return kq

	# Ứng suất pháp tuyến SAU khi Neo
	def ungsuatphap1(self, bk):
		hs_A = self.hs_A()
		hs_D = self.hs_D()
		r = bk  # self.r
		a = self.ct_R
		b = a + self.n_L
		P = self.d_tltt * self.ct_H

		if a < r and r < b:
			# CT 5.5 trang 2 -tac gia Cong. Vung duoc neo
			kq = (P / hs_D) * ((1 / (r ** 2)) + (3 * hs_A / (2 * r ** 4)) + (hs_A / (2 * a ** 4)) + (1 / a ** 2))
		elif r >= b:
			# CT 5.7 trang 2 -tac gia Cong. Ngoai vung duoc neo
			kq = P + (P / hs_D) * (1 + hs_A / (b ** 2)) * (1 / (r ** 2))
		elif r <= a:
			# Trong long CTN
			kq = 0

		return kq

	# Ứng suất tiếp tuyến TRƯỚC khi Neo
	def ungsuattiep0(self, bk):
		r = bk  # self.r
		R = self.ct_R
		if r >= R:
			P = self.d_tltt * self.ct_H
			# CT trang 77 -tac gia Phich. Ung suat tiep truoc khi neo
			kq = P * (1 + (R / r) ** 2)
		else:
			kq = 0

		return kq

	# Ứng suất tiếp tuyến SAU khi Neo
	def ungsuattiep1(self, bk):
		hs_A = self.hs_A()
		hs_D = self.hs_D()
		r = bk  # self.r
		a = self.ct_R
		b = a + self.n_L
		P = self.d_tltt * self.ct_H
		if a < r < b:
			# CT 5.4 trang 2 -tac gia Cong. Vung duoc neo
			kq = (-P / hs_D) * ((1 / (r ** 2)) + (hs_A / (2 * r ** 4)) - (hs_A / (2 * a ** 4)) - (1 / a ** 2))
		elif r >= b:
			# CT 5.6 trang 2 -tac gia Cong. Ngoai vung duoc neo
			kq = P - (P / hs_D) * (1 + hs_A / (b ** 2)) * (1 / (r ** 2))
		elif r <= a:
			# Trong long CTN
			kq = 0

		#print("Ket qua", kq)
		return kq

	# Chuyển vị TRƯỚC khi Neo
	def chuyenvi0(self, bk):
		r = bk  # self.r
		R = self.ct_R
		if r >= R:
			P = self.d_tltt * self.ct_H
			E0 = self.d_E0
			# CT trang 77 -tac gia Phich. Chuyen vi truoc khi neo
			kq = 3 * P * (R ** 2) / (2 * E0 * r)
		else:
			kq = 0
		return kq

	# Chuyển vị SAU khi Neo
	def chuyenvi1(self, bk):
		En 		= self.E1(bk)
		hs_A 	= self.hs_A()
		hs_D 	= self.hs_D()
		r 		= bk  # self.r
		a 		= self.ct_R
		b 		= a + self.n_L
		P 		= self.d_tltt * self.ct_H
		
		if a < r < b:
			# CT 5.8 trang 2 -tac gia Cong. Vung duoc neo
			kq = (3 * P / (2 * En * hs_D)) * (1 / r + (hs_A / (r ** 3)))
		elif r >= b:
			# CT 5.9 trang 2 -tac gia Cong. Ngoai vung duoc neo
			kq = (3 * P * r / (2 * En * hs_D)) * (1 + (hs_A / (b ** 2)))
		elif r <= a:
			# Trong long CTN
			kq = 0

		return kq

	# Biến dạng TRƯỚC khi Neo
	def biendang0(self, bk):
		r 		= bk  # self.r
		R 		= self.ct_R
		
		if r >= R:
			cv = self.chuyenvi0(bk)
			kq = cv / r
		else:
			kq = 0
		return kq

	# Biến dạng SAU khi Neo
	def biendang1(self, bk):
		r 		= bk  # self.r
		R 		= self.ct_R
		
		if r >= R:
			cv = self.chuyenvi1(bk)
			kq = cv / r
		else:
			kq = 0
		return kq
	
	# Modul đàn hồi TRƯỚC khi Neo
	def moduldanhoi0(self, bk):
		r 		= bk  # self.r
		R 		= self.ct_R
		
		if r >= R:
			kq = self.d_E0
		else:
			kq = 0
		return kq

# Nguyên lý 4 : Tính khối NÊM
class NguyenLy4:
	def __init__(self, gd_1, gpv_1, tkn_1, gd_2, gpv_2, tkn_2, gd_3, gpv_3, tkn_3, gd_ctn, gpv_ctn, cr_ctn,
				 tt_khoi_nem):
		self.goc_doc_1 							= gd1
		self.goc_phuong_vi_1 					= gpv_1
		self.ten_khe_nut_1 						= tkn_1

		self.goc_doc_2 							= gd2
		self.goc_phuong_vi_2 					= gpv_2
		self.ten_khe_nut_2 						= tkn_2

		self.goc_doc_3 							= gd3
		self.goc_phuong_vi_3 					= gpv_3
		self.ten_khe_nut_3 						= tkn_3

		self.goc_doc__cong_trinh_ngam 			= gd_ctn
		self.goc_phuong_vi__cong_trinh_ngam 	= gpv_ctn 
		self.chieu_rong_cong_trinh_ngam 		= cr_ctn

		self.the_tich_khoi_nem 					= tt_khoi_nem


# Nguyên lý 5 : Nguyên lý Tương tac
# Gg : modul đàn hồi trượt của vữa Neo
class NguyenLy5:
	def __init__(self, Db, Dh, Eb, L, Oc, Em, Um, P0, Ra, Gg, Gm):
		N 	= 1  # Chưa xác thực
		Pi 	= 1  # Chưa xác thực
		R 	= 1  # Chưa xác thực
		S 	= 1  # Chưa xác thực

		Oc_sao 		= 0.65 * (Oc ** 0.8)
		Os 			= Oc - Oc_sao
		phi 		= 38.28 * (Oc ** -0.004)
		lan_da 		= 1.33 * (Oc ** 0.153)
		h 			= 1.88 * (Oc ** 0.136)
		f 			= 1.41 * (Oc ** 0.035)
		
		#phi_sao 	= phi - 6.0 			 #todo : Phịa
		#h 			= (1 + sin(radians(phi_sao))) / (1 - sin(radians(phi_sao)))
		
		Rb = Db / 2
		Rg = Dh / 2
		
		##### Vùng dẻo
		H = (2 * math.pi * Gg * Gm) / ((math.log(R / Rb)) * Gg + (math.log(Rg / Rb)) * Gm)

		if H == 0:  # H = 0 : error : check lai Cong thuc
			H = 34
		Kp = (1 + sin(radians(phi))) / (1 - sin(radians(phi)))
		print("Kp", Kp)

		ep_xi_lon = 2 / (lan_da * (1 + h) + (h-1) ** (1 / (1 + h)))  # todo:  (1-h) -> (h - 1)
		ep_xi_lon = 0.08											 # Phịa
		
		# print("Ra", Ra)
		#print("ep_xi_lon", ep_xi_lon)
		# print("Ra / ep_xi_lon", (Ra / ep_xi_lon))
		# print("((N * ep_xi_lon**(Kp-1)) * (1 - Kp) * (h + Kp) + Os*(1 + h) + 2/(lan_da - 1))",
			  # ((N * ep_xi_lon ** (Kp - 1)) * (1 - Kp) * (h + Kp) + Os * (1 + h) + 2 / (lan_da - 1)))
		# print("((1 - Kp) * (h + Kp)*Pi - Oc_sao * (h + Kp))", ((1 - Kp) * (h + Kp) * Pi - Oc_sao * (h + Kp)))

		# Re = (Ra / ep_xi_lon) * (((N * ep_xi_lon ** (Kp - 1)) * (1 - Kp) * (h + Kp) + Os * (1 + h) + 2 / (
		# lan_da - 1)) / ((1 - Kp) * (h + Kp) * Pi - Oc_sao * (h + Kp))) ** (1 / (Kp - 1))
		
		Re = 4.3 * Ra * 2
		# print("Re", Re)
		Rf = ep_xi_lon * Re

		B0 = (1 + Um) * Em * (P0 * (Kp - 1) + Oc) / (Kp + 1)

		U3 = (2 * B0 / (1 + f)) * (Rf / Re) ** -(1 + h)

		U2 = 2 * B0 * (f - h) / ((1 + h) * (1 + f))

		U1 = B0 * (h - 1) / (1 + h)

		C1 = -H * U3 * ep_xi_lon ** (1 + h) * Re ** (1 + f) * f

		B1 = -H * (U1 + U2 * ep_xi_lon ** -(1 + h))

		# Ab : Dien tich mat cat ngang
		Ab = math.pi * (Rg ** 2)
		an_pha = ((1 / Ab * Eb) + 1 / (S * Em)) * H

		## END Vùng dẻo

		##### Vùng Giảm bền
		C2 = (-2 * h * B0 * H * Re ** (1 + h)) / (1 + h)

		B2 = (H * B0 * (1 - h)) / (1 + h)
		## END Vùng Giảm bền

		##### Vùng Đàn hồi
		Oe = (2 * P0 - Oc) / (Kp + 1)

		C3 = (1 + Um) / (Em * ((P0 - Oe) * (Ra ** 2)) * H)
		
		B3 = 0
		## END Vùng Đàn hồi

		# Vị trí trung hòa ứng suất dọc neo
		p = L / (math.log(1 + (L / Ra)))

		
		### Gán dữ liệu tính toán
		self.H 			= H
		self.Kp 		= Kp
		self.ep_xi_lon 	= ep_xi_lon
		self.Re 		= Re
		self.Rf 		= Rf
		self.B0 		= B0
		self.U3 		= U3
		self.U2 		= U2
		self.U1 		= U1
		self.C1 		= C1
		self.B1 		= B1
		self.Ab 		= Ab
		self.an_pha 	= an_pha

		self.C2 		= C2
		self.B2 		= B2

		self.Oe 		= Oe
		self.C3 		= C3
		self.p 			= p
		# print("p", p)
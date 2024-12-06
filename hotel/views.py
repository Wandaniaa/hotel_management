from datetime import datetime
import logging
from weasyprint import HTML
import csv
from django.db.models import Q
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Cast
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404 
from .models import CleaningLog, InventoryItem
from .forms import InventoryItemForm
from .models import Room, RoomType, Hall
from .forms import RoomForm, RoomTypeForm, HallForm
from .models import Layanan, KategoriLayanan, Tamu, CheckIn
from .forms import LayananForm, KategoriLayananForm, TamuForm
from .forms import CheckInForm
from decimal import Decimal
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from io import BytesIO
from django.contrib import messages
from django.urls import reverse
from .models import Checkout
from .models import RoomService
from .forms import RoomServiceForm
from django.utils.timezone import now
from django.db import transaction
import csv

from hotel import models

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('base')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

from django.db.models import Q

def base_view(request):
    # Ambil data kamar
    total_kamar = Room.objects.count()
    kamar_terpakai = Room.objects.filter(status='Tidak Tersedia').count()
    kamar_tersedia = Room.objects.filter(status='Tersedia').count()
    kamar_kotor = Room.objects.filter(status='maintenance').count()
    kamar_kotor_list = Room.objects.filter(status='maintenance')  # Daftar kamar kotor

    # Ambil data aula
    total_aula = Hall.objects.count()
    aula_dipesan = Hall.objects.filter(status='reserved').count()
    aula_tersedia = Hall.objects.filter(status='available').count()
    aula_perawatan = Hall.objects.filter(status='maintenance').count()
    aula_perawatan_list = Hall.objects.filter(status='maintenance')  # Daftar aula dalam perawatan

    # Hitung persentase kamar terpakai
    persentase_kamar_terpakai = (kamar_terpakai / total_kamar * 100) if total_kamar > 0 else 0

    # Ambil log pembersihan untuk kamar atau aula yang sudah checkout dan berstatus maintenance
    cleaning_logs = CleaningLog.objects.filter(
        Q(cleaned_room__status='maintenance', cleaned_room__checkin__status_checkout=True) |
        Q(cleaned_hall__status='maintenance', cleaned_hall__checkin__status_checkout=True)
    )

    # Tamu Menginap (tamu yang belum checkout)
    tamu_menginap = CheckIn.objects.filter(status_checkout=False)

    # Tamu Checkout (gunakan tamu_menginap agar datanya sama)
    tamu_checkout = tamu_menginap

    context = {
        # Data Kamar
        'total_kamar': total_kamar,
        'kamar_terpakai': kamar_terpakai,
        'kamar_tersedia': kamar_tersedia,
        'kamar_kotor': kamar_kotor,
        'kamar_kotor_list': kamar_kotor_list,  # Tambahkan ke context
        'persentase_kamar_terpakai': round(persentase_kamar_terpakai, 2),

        # Data Aula
        'total_aula': total_aula,
        'aula_dipesan': aula_dipesan,
        'aula_tersedia': aula_tersedia,
        'aula_perawatan': aula_perawatan,
        'aula_perawatan_list': aula_perawatan_list,  # Tambahkan ke context

        # Tamu Menginap & Tamu Checkout
        'tamu_menginap': tamu_menginap,
        'tamu_checkout': tamu_checkout,

        # Catatan Pembersihan
        'cleaning_logs': cleaning_logs,
    }

    return render(request, 'base.html', context)

# Menampilkan daftar user
@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

# Menambahkan user baru
@login_required
def add_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'add_user.html', {'form': form})

# Mengedit user (opsional)
@login_required
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreationForm(instance=user)
    return render(request, 'edit_user.html', {'form': form})

# Menghapus user
@login_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'delete_user.html', {'user': user})

def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, 'inventory_list.html', {'items': items})

def add_inventory(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')  # Redirect to the inventory list page
    else:
        form = InventoryItemForm()
    return render(request, 'add_inventory.html', {'form': form})

def inventory_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory_edit.html', {'form': form})

def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory_list')
    return render(request, 'inventory_delete.html', {'item': item})

def barang_terpakai(request):
    items = InventoryItem.objects.all()
    return render(request, 'barang_terpakai.html', {'items': items})

def barang_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('barang_terpakai')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'barang_edit.html', {'form': form})

def barang_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('barang_terpakai')
    return render(request, 'barang_delete.html', {'item': item})

def persediaan_barang(request):
    items = InventoryItem.objects.all()
    return render(request, 'persediaan_barang.html', {'items': items})

# View Kamar
def room_list(request):
    rooms = Room.objects.all()
    for room in rooms:
        room.refresh_from_db()  # Memastikan data diperbarui dari database

    return render(request, 'room_list.html', {'rooms': rooms})


def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'add_room.html', {'form': form})

def edit_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'edit_room.html', {'form': form})

def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('room_list')
    return render(request, 'delete_room.html', {'room': room})

# View untuk daftar tipe kamar
def room_type_list(request):
    room_types = RoomType.objects.all()
    return render(request, 'room_type_list.html', {'room_types': room_types})

# View untuk menambah tipe kamar
def add_room_type(request):
    if request.method == 'POST':
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_type_list')
    else:
        form = RoomTypeForm()
    return render(request, 'add_room_type.html', {'form': form})

# View untuk mengedit tipe kamar
def edit_room_type(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    if request.method == 'POST':
        form = RoomTypeForm(request.POST, instance=room_type)
        if form.is_valid():
            form.save()
            return redirect('room_type_list')
    else:
        form = RoomTypeForm(instance=room_type)
    return render(request, 'edit_room_type.html', {'form': form})

# View untuk menghapus tipe kamar
def delete_room_type(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    if request.method == 'POST':
        room_type.delete()
        return redirect('room_type_list')
    return render(request, 'delete_room_type.html', {'room_type': room_type})

# View untuk daftar aula
def hall_list(request):
    halls = Hall.objects.all()
    for hall in halls:
        hall.refresh_from_db()  # Memastikan data terbaru dari database

    return render(request, 'hall_list.html', {'halls': halls})

# View untuk menambahkan aula
def add_hall(request):
    if request.method == 'POST':
        form = HallForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hall_list')
    else:
        form = HallForm()
    return render(request, 'add_hall.html', {'form': form})

# View untuk mengedit aula
def edit_hall(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    if request.method == 'POST':
        form = HallForm(request.POST, instance=hall)
        if form.is_valid():
            form.save()
            return redirect('hall_list')
    else:
        form = HallForm(instance=hall)
    return render(request, 'edit_hall.html', {'form': form})

# View untuk menghapus aula
def delete_hall(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    if request.method == 'POST':
        hall.delete()
        return redirect('hall_list')
    return render(request, 'delete_hall.html', {'hall': hall})

# List Layanan
def layanan_list(request):
    layanan = Layanan.objects.all()
    return render(request, 'layanan_list.html', {'layanan': layanan})

def add_layanan(request):
    if request.method == 'POST':
        form = LayananForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('layanan_list')
    else:
        form = LayananForm()
    return render(request, 'add_layanan.html', {'form': form})

def edit_layanan(request, pk):
    layanan = get_object_or_404(Layanan, pk=pk)
    if request.method == 'POST':
        form = LayananForm(request.POST, instance=layanan)
        if form.is_valid():
            form.save()
            return redirect('layanan_list')
    else:
        form = LayananForm(instance=layanan)
    return render(request, 'edit_layanan.html', {'form': form})

def delete_layanan(request, pk):
    layanan = get_object_or_404(Layanan, pk=pk)
    if request.method == 'POST':
        layanan.delete()
        return redirect('layanan_list')
    return render(request, 'delete_layanan.html', {'layanan': layanan})

# List Kategori Layanan
def kategori_layanan_list(request):
    kategori_layanan = KategoriLayanan.objects.all()
    return render(request, 'kategori_layanan_list.html', {'kategori_layanan': kategori_layanan})

def add_kategori_layanan(request):
    if request.method == 'POST':
        form = KategoriLayananForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kategori_layanan_list')
    else:
        form = KategoriLayananForm()
    return render(request, 'add_kategori_layanan.html', {'form': form})

def edit_kategori_layanan(request, pk):
    kategori_layanan = get_object_or_404(KategoriLayanan, pk=pk)
    if request.method == 'POST':
        form = KategoriLayananForm(request.POST, instance=kategori_layanan)
        if form.is_valid():
            form.save()
            return redirect('kategori_layanan_list')
    else:
        form = KategoriLayananForm(instance=kategori_layanan)
    return render(request, 'edit_kategori_layanan.html', {'form': form})

def delete_kategori_layanan(request, pk):
    kategori_layanan = get_object_or_404(KategoriLayanan, pk=pk)
    if request.method == 'POST':
        kategori_layanan.delete()
        return redirect('kategori_layanan_list')
    return render(request, 'delete_kategori_layanan.html', {'kategori_layanan': kategori_layanan})

def tamu_list(request):
    tamu = Tamu.objects.all()
    return render(request, 'tamu_list.html', {'tamu_list': tamu})

def add_tamu(request):
    if request.method == 'POST':
        form = TamuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tamu_list')
    else:
        form = TamuForm()
    return render(request, 'add_tamu.html', {'form': form})

def edit_tamu(request, pk):
    tamu = get_object_or_404(Tamu, pk=pk)
    if request.method == 'POST':
        form = TamuForm(request.POST, instance=tamu)
        if form.is_valid():
            form.save()
            return redirect('tamu_list')
    else:
        form = TamuForm(instance=tamu)
    return render(request, 'edit_tamu.html', {'form': form})

def delete_tamu(request, pk):
    tamu = get_object_or_404(Tamu, pk=pk)
    if request.method == 'POST':
        tamu.delete()
        return redirect('tamu_list')
    return render(request, 'delete_tamu.html', {'tamu': tamu})

# def check_in_view(request):
#     if request.method == 'POST':
#         form = CheckInForm(request.POST)
#         if form.is_valid():
#             check_in = form.save(commit=False)

#             # Mengambil harga kamar atau aula untuk perhitungan PPN
#             if check_in.kamar:
#                 room = get_object_or_404(Room, id=check_in.kamar.id)
#                 check_in.total_harga = room.tipe_kamar.harga  # Simpan harga kamar
#                 room.check_in()  # Lakukan check-in pada kamar

#             elif check_in.aula:
#                 hall = get_object_or_404(Hall, id=check_in.aula.id)
#                 check_in.total_harga = hall.harga  # Simpan harga aula
#                 hall.reserve()  # Lakukan reservasi pada aula

#             check_in.save()  # Simpan data check-in setelah semua diisi

#             # Alihkan ke halaman invoice atau halaman lain
#             return render(request, 'invoice.html', {'check_in': check_in})

#     else:
#         form = CheckInForm()

#     # Mengambil semua tamu, kamar, dan aula untuk form
#     tamu_list = Tamu.objects.all()
#     rooms = Room.objects.all()
#     halls = Hall.objects.all()

#     return render(request, 'check_in.html', {
#         'form': form,
#         'tamu_list': tamu_list,
#         'rooms': rooms,
#         'halls': halls,
#         'jumlah_tamu': range(0, 5)  # Misalnya batas maksimum tamu
#     })


def check_in_view(request):
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            check_in = form.save(commit=False)

            # Cek apakah kamar atau aula dipilih untuk check-in
            if check_in.kamar:
                room = get_object_or_404(Room, id=check_in.kamar.id)
                check_in.total_harga = room.tipe_kamar.harga  # Simpan harga kamar
                room.check_in()  # Ubah status kamar menjadi "Tidak Tersedia"
                
                check_in.save()  # Pastikan check_in disimpan sebelum merender invoice

                return render(request, 'invoice.html', {'check_in': check_in})

            elif check_in.aula:
                hall = get_object_or_404(Hall, id=check_in.aula.id)
                check_in.total_harga = hall.harga  # Simpan harga aula
                hall.reserve()  # Ubah status aula menjadi "Dipesan"

                check_in.save()  # Pastikan check_in disimpan sebelum merender invoice

                return render(request, 'invoice.html', {'check_in': check_in})

    else:
        form = CheckInForm()

    tamu_list = Tamu.objects.all()

    # Mengambil semua kamar dan aula yang belum di-check-in
    rooms = Room.objects.filter(status='Tersedia')  # Hanya kamar yang tersedia
    halls = Hall.objects.filter(status='available')  # Ubah status menjadi 'available' untuk aula yang tersedia

    return render(request, 'check_in.html', {
        'form': form,
        'tamu_list': tamu_list,
        'rooms': rooms,
        'halls': halls
    })
   
logger = logging.getLogger(__name__)

def check_out_view(request):
    if request.method == 'POST':
        if 'checkout_id' in request.POST:
            checkout_id = request.POST.get('checkout_id')
            payment = Decimal(request.POST.get('payment'))

            try:
                # Coba untuk mendapatkan objek Checkout
                checkout = Checkout.objects.get(id=checkout_id)
            except (Checkout.DoesNotExist, ValueError) as e:
                logger.error(f"Error saat mendapatkan checkout: {e}")
                return render(request, 'invoice_checkout.html', {'error': 'Terjadi kesalahan pada pembayaran.'})

            # Validasi pembayaran
            if payment <= 0:
                logger.warning(f"Pembayaran tidak valid: {payment}")
                return render(request, 'invoice_checkout.html', {'error': 'Pembayaran harus lebih dari 0.'})

            # Proses pembayaran
            try:
                with transaction.atomic():
                    kembalian = checkout.bayar(payment)  # Update status pembayaran dan sisa pembayaran

                    # Segarkan data checkout untuk memastikan status dan sisa pembayaran yang terbaru
                    checkout.refresh_from_db()
                    logger.info(f"Pembayaran berhasil, sisa pembayaran setelah pembayaran: {checkout.sisa_pembayaran}")

                    return render(request, 'invoice_checkout.html', {
                        'checkout': checkout,
                        'success': 'Pembayaran berhasil. Terima kasih!',
                        'kembalian': kembalian,  # Menampilkan kembalian
                    })
            except Exception as e:
                logger.error(f"Error saat memproses pembayaran: {e}")
                return render(request, 'invoice_checkout.html', {
                    'checkout': checkout,
                    'error': 'Terjadi kesalahan saat memproses pembayaran.',
                })
        
        # Proses checkout awal jika tidak ada checkout_id
        else:
            check_in_id = request.POST.get('check_in_id')
            try:
                check_in_id = int(check_in_id)
                logger.info(f"Check-in ID diterima: {check_in_id}")
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing check-in ID: {e}")
                return render(request, 'check_out.html', {'error': 'Check-in ID harus berupa angka yang valid'})

            check_in = get_object_or_404(CheckIn, id=check_in_id)

            # Membuat objek checkout baru
            checkout = Checkout(
                check_in=check_in,
                kamar=check_in.kamar,
                aula=check_in.aula,
                tanggal_checkout=timezone.now()
            )

            # Hitung biaya menginap
            if checkout.kamar:
                durasi_menginap = (checkout.tanggal_checkout - check_in.tanggal_check_in).total_seconds() / 3600
                harga_per_malam = Decimal(checkout.kamar.tipe_kamar.harga)
                total_harga_menginap = harga_per_malam * Decimal(durasi_menginap // 24 + (1 if durasi_menginap % 24 > 0 else 0))
                checkout.kamar.check_out()
                logger.info(f"Biaya menginap kamar: {total_harga_menginap}")
            elif checkout.aula:
                total_harga_menginap = Decimal(checkout.aula.harga)
                checkout.aula.check_out()
                logger.info(f"Biaya menginap aula: {total_harga_menginap}")

            # Ambil layanan terkait
            layanan_terkait = RoomService.objects.filter(check_in=check_in)
            total_biaya_layanan = layanan_terkait.aggregate(total=models.Sum('harga_layanan'))['total'] or Decimal(0)

            # Total biaya checkout (menginap + layanan)
            total_biaya_checkout = total_harga_menginap + total_biaya_layanan
            logger.info(f"Total biaya checkout: {total_biaya_checkout}")

            # Simpan data ke model Checkout
            checkout.total_harga = total_biaya_checkout
            checkout.sisa_pembayaran = max(total_biaya_checkout - check_in.deposit, 0)
            checkout.status_pembayaran = 'Lunas' if checkout.sisa_pembayaran == 0 else 'Belum Lunas'
            checkout.save()
            logger.info(f"Data checkout disimpan, sisa pembayaran: {checkout.sisa_pembayaran}")

            # Tandai check-in sudah checkout
            check_in.status_checkout = True
            check_in.save()
            logger.info(f"Check-in dengan ID {check_in.id} telah selesai checkout")

            return render(request, 'invoice_checkout.html', {
                'checkout': checkout,
                'nama_tamu': check_in.nama_tamu.nama,
                'tanggal_check_in': check_in.tanggal_check_in,
                'tanggal_check_out': checkout.tanggal_checkout,
                'layanan_terkait': layanan_terkait,
                'total_harga_layanan': total_biaya_layanan,
                'total_harga': checkout.total_harga,
                'sisa_pembayaran': checkout.sisa_pembayaran,
            })

    # Menampilkan daftar check-in yang belum checkout
    check_ins = CheckIn.objects.filter(status_checkout=False)
    return render(request, 'check_out.html', {'check_ins': check_ins})

# def check_out_view(request):
#     if request.method == 'POST':
#         check_in_id = request.POST.get('check_in_id')

#         try:
#             check_in_id = int(check_in_id)
#         except (ValueError, TypeError):
#             return render(request, 'check_out.html', {'error': 'Check-in ID harus berupa angka yang valid'})

#         check_in = get_object_or_404(CheckIn, id=check_in_id)

#         # Buat objek Checkout dengan data yang diperlukan
#         checkout = Checkout(
#             check_in=check_in,
#             kamar=check_in.kamar,
#             aula=check_in.aula,
#             tanggal_checkout=timezone.now()
#         )

#         # Harga per malam atau per sewa
#         if checkout.kamar:
#             durasi_menginap = (checkout.tanggal_checkout - check_in.tanggal_check_in).total_seconds() / 3600
#             harga_per_malam = Decimal(checkout.kamar.tipe_kamar.harga)
#             total_harga_menginap = harga_per_malam * Decimal(durasi_menginap // 24 + (1 if durasi_menginap % 24 > 0 else 0))
#         elif checkout.aula:
#             total_harga_menginap = Decimal(checkout.aula.harga)
#         else:
#             total_harga_menginap = Decimal(0)

#         # Hitung PPN dan total harga
#         checkout.ppn = total_harga_menginap * Decimal('0.11')
#         total_harga_sebelum_deposit = total_harga_menginap + checkout.ppn
#         checkout.total_harga = max(total_harga_sebelum_deposit - check_in.deposit, Decimal(0))
#         checkout.sisa_pembayaran = checkout.total_harga
#         checkout.status_pembayaran = 'Lunas' if checkout.sisa_pembayaran == 0 else 'Belum Lunas'
        
#         # Simpan objek Checkout
#         checkout.save()

       
#         check_in.status_checkout = True
#         check_in.save()
       
#         return render(request, 'invoice_checkout.html', {
#             'checkout': checkout,
#             'nama_tamu': check_in.nama_tamu.nama,
#             'tanggal_check_in': check_in.tanggal_check_in,
#             'tanggal_check_out': checkout.tanggal_checkout,
#             'total_harga': checkout.total_harga,
#             'sisa_pembayaran': checkout.sisa_pembayaran,
#         })
    
#     check_ins = CheckIn.objects.filter(status_checkout=False)
#     return render(request, 'check_out.html', {'check_ins': check_ins})

def tamu_in_house_view(request):
    # Ambil semua CheckIn yang statusnya belum di-checkout
    in_house_guests = CheckIn.objects.filter(status_checkout=False)

    # Tambahkan informasi durasi menginap dan room service untuk setiap tamu in-house
    for guest in in_house_guests:
        # Menghitung durasi menginap
        durasi = timezone.now() - guest.tanggal_check_in
        guest.durasi_menginap_hari = durasi.days
        guest.durasi_menginap_jam = durasi.seconds // 3600
        
        # Ambil semua layanan room service yang terkait dengan check_in tamu
        room_services = RoomService.objects.filter(check_in=guest).select_related('layanan')

        # Menambahkan informasi layanan kamar ke objek tamu
        guest.room_services = room_services

    # Kirim data tamu beserta layanan kamar yang dipesan ke template
    return render(request, 'tamu_in_house.html', {
        'in_house_guests': in_house_guests,
    })

def edit_tamu_in_house_view(request, id):
    tamu = get_object_or_404(CheckIn, id=id)  # Ambil data CheckIn yang ingin diedit
    
    if request.method == 'POST':
        form = CheckInForm(request.POST, instance=tamu)
        if form.is_valid():
            # Simpan perubahan pada CheckIn
            tamu = form.save()

            # Tangani layanan kamar yang dipilih
            layanan_terpilih = form.cleaned_data['layanan']
            # Hapus layanan yang tidak dipilih lagi
            RoomService.objects.filter(check_in=tamu).exclude(layanan__in=layanan_terpilih).delete()

            # Tambahkan layanan yang baru dipilih
            for layanan in layanan_terpilih:
                if not RoomService.objects.filter(check_in=tamu, layanan=layanan).exists():
                    RoomService.objects.create(check_in=tamu, layanan=layanan)

            return redirect('tamu_in_house')  # Redirect setelah menyimpan
    else:
        form = CheckInForm(instance=tamu)

    return render(request, 'edit_tamu_in_house.html', {'form': form, 'tamu': tamu})

def tambah_room_service(request):
    if request.method == 'POST':
        form = RoomServiceForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            kategori_layanan = form.cleaned_data['kategori_layanan']
            layanan = form.cleaned_data['layanan']

            if not RoomService.objects.filter(check_in=check_in, kategori_layanan=kategori_layanan, layanan=layanan).exists():
                form.save()
                return redirect('room_service_success')  # Atur URL setelah berhasil submit
            else:
                form.add_error(None, "Layanan sudah ada untuk check-in ini.")  # Menambahkan error jika ada duplikasi
    else:
        form = RoomServiceForm()

    return render(request, 'tambah_room_service.html', {
        'form': form,
    })

def room_service_success(request):
    return render(request, 'room_service_success.html')

@login_required
def cleaning_list_view(request):
    # Filter untuk hanya kamar/aula dalam perawatan
    rooms = Room.objects.filter(status='maintenance')
    halls = Hall.objects.filter(status='maintenance')

    # Filter berdasarkan query params (opsional)
    start_date = request.GET.get('start_date')
    if start_date:
        rooms = rooms.filter(updated_at__gte=start_date)
        halls = halls.filter(updated_at__gte=start_date)

    return render(request, 'cleaning_list.html', {'rooms': rooms, 'halls': halls})

@login_required
def mark_cleaned_view(request, room_or_hall, id):
    obj = None
    if room_or_hall == 'room':
        obj = get_object_or_404(Room, id=id)
    elif room_or_hall == 'hall':
        obj = get_object_or_404(Hall, id=id)

    # Validasi apakah objek dalam status 'maintenance'
    if obj.status != 'maintenance':
        messages.error(request, f"{obj} tidak dalam status 'Dalam Perawatan'.")
        return redirect('cleaning_list')

    if request.method == 'POST':
        # Simpan catatan jika ada
        note = request.POST.get('note', '')

        # Gunakan metode selesai_perawatan untuk mengubah status
        obj.selesai_perawatan()

        # Rekam log
        CleaningLog.objects.create(
            user=request.user,
            cleaned_room=obj if room_or_hall == 'room' else None,
            cleaned_hall=obj if room_or_hall == 'hall' else None,
            note=note
        )

        messages.success(request, f"{obj} telah ditandai selesai dibersihkan.")
        return redirect('cleaning_list')

    return render(request, 'mark_cleaned.html', {'obj': obj, 'type': room_or_hall})

@login_required
def cleaning_history_view(request):
    logs = CleaningLog.objects.all().order_by('-timestamp')
    return render(request, 'cleaning_history.html', {'logs': logs})

@login_required
def export_cleaning_log(request):
    logs = CleaningLog.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cleaning_log.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Timestamp', 'Room', 'Hall', 'Note'])
    for log in logs:
        writer.writerow([log.user, log.timestamp, log.cleaned_room, log.cleaned_hall, log.note])

    return response

#view laporan kamar
@login_required
def room_report_view(request):
    rooms = Room.objects.all()
    return render(request, 'room_report.html', {'rooms': rooms})

@login_required
def export_room_report(request):
    rooms = Room.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="room_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['No Kamar', 'Tipe Kamar', 'Status'])
    for room in rooms:
        writer.writerow([room.no_kamar, room.tipe_kamar.nama, room.status])

    return response

#view laporan checkin
@login_required
def checkin_report_view(request):
    checkins = CheckIn.objects.all()
    return render(request, 'checkin_report.html', {'checkins': checkins})

@login_required
def export_checkin_report(request):
    checkins = CheckIn.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="checkin_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID Check-In', 'Nama Tamu', 'Jenis Kelamin', 'Jumlah Dewasa', 'Jumlah Anak',
        'Tanggal Check-In', 'Tanggal Check-Out', 'Deposit', 'Total Harga', 
        'VAT', 'Total Harus Dibayar', 'Status Check-Out', 'Kamar', 'Aula'
    ])
    for checkin in checkins:
        kamar = checkin.kamar.no_kamar if checkin.kamar else '—'
        aula = checkin.aula.nama if checkin.aula else '—'
        writer.writerow([
            checkin.id,
            checkin.nama_tamu.nama,
            dict(CheckIn.GENDER_CHOICES).get(checkin.jenis_kelamin, '-'),
            checkin.jumlah_dewasa,
            checkin.jumlah_anak,
            checkin.tanggal_check_in,
            checkin.tanggal_check_out,
            checkin.deposit,
            checkin.total_harga,
            checkin.vat,
            checkin.total_harus_dibayar,
            'Selesai' if checkin.status_checkout else 'Belum',
            kamar,
            aula
        ])

    return response

#view laporan checkout
@login_required
def checkout_report_view(request):
    checkouts = Checkout.objects.all()
    return render(request, 'checkout_report.html', {'checkouts': checkouts})

@login_required
def export_checkout_report(request):
    checkouts = Checkout.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="checkout_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Check-Out', 'Nama Tamu', 'Tanggal Check-Out', 'Total Harga'])
    for checkout in checkouts:
        writer.writerow([checkout.id, checkout.check_in.nama_tamu, checkout.tanggal_checkout, checkout.total_harga])

    return response

#view laporan aula
@login_required
def hall_report_view(request):
    halls = Hall.objects.all()
    return render(request, 'hall_report.html', {'halls': halls})

@login_required
def export_hall_report(request):
    halls = Hall.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hall_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nama Aula', 'Status'])
    for hall in halls:
        writer.writerow([hall.nama, hall.status])

    return response

#view laporan pembersihan
@login_required
def cleaning_log_report_view(request):
    cleaning_logs = CleaningLog.objects.all()
    return render(request, 'cleaning_log_report.html', {'cleaning_logs': cleaning_logs})

@login_required
def export_cleaning_log_report(request):
    cleaning_logs = CleaningLog.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cleaning_log_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Timestamp', 'Kamar', 'Aula', 'Catatan'])
    for log in cleaning_logs:
        writer.writerow([
            log.user.username,
            log.timestamp,
            log.cleaned_room.no_kamar if log.cleaned_room else '',
            log.cleaned_hall.nama if log.cleaned_hall else '',
            log.note,
        ])

    return response

@login_required
def logout_view(request):
    print("Logout initiated")  # Debug untuk memastikan fungsi dipanggil
    logout(request)  # Melakukan logout
    print("Logout completed")  # Debug untuk memastikan logout berhasil
    return redirect('home')
from django.contrib import admin
from .models import InventoryItem
from .models import Tamu
from .models import CheckIn
from .models import Checkout, Room, Hall
from .models import Layanan, KategoriLayanan, CleaningLog

admin.site.register(Tamu)

class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'check_in', 'kamar', 'aula', 'total_harga', 'status_pembayaran', 'tanggal_checkout')

admin.site.register(Checkout, CheckoutAdmin)

admin.site.register(CheckIn)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('no_kamar', 'tipe_kamar', 'status')  # Sesuaikan field yang ingin ditampilkan
    search_fields = ('no_kamar', 'tipe_kamar__nama')  # Jika ada field terkait di tipe_kamar

admin.site.register(Room, RoomAdmin)

class HallAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kapasitas', 'status')
    search_fields = ('nama',)

admin.site.register(Hall, HallAdmin)

# Register your models here.
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tanggal_pembelian',
        'no_po_nota',
        'nama_supplier',
        'nama_barang',
        'satuan',
        'harga_satuan',
        'jumlah',
        'total_harga',
        'keterangan',
        
    )
    search_fields = ('nama_barang', 'no_po_nota', 'nama_supplier')
    list_filter = ('tanggal_pembelian', 'satuan')
    ordering = ('-tanggal_pembelian',)
    list_per_page = 20

admin.site.register(InventoryItem, InventoryItemAdmin)

@admin.register(Layanan)
class LayananAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kategori_layanan', 'harga', 'satuan')  # Kolom yang ingin ditampilkan di daftar
    search_fields = ('nama',)  # Memungkinkan pencarian berdasarkan nama layanan

@admin.register(KategoriLayanan)  # Jika Anda juga ingin mendaftarkan kategori layanan
class KategoriLayananAdmin(admin.ModelAdmin):
    list_display = ('nama',)

class CleaningLogAdmin(admin.ModelAdmin):
    # Kolom yang akan ditampilkan di daftar admin
    list_display = ('user', 'cleaned_room', 'cleaned_hall', 'timestamp', 'note')
    
    # Kolom yang bisa dicari di admin
    search_fields = ('user__username', 'cleaned_room__no_kamar', 'cleaned_hall__nama', 'note')
    
    # Filter berdasarkan tanggal atau status
    list_filter = ('timestamp',)
    
    # Fitur pengurutan berdasarkan timestamp
    ordering = ('-timestamp',)
    
    # Menambahkan opsi untuk menghapus banyak item sekaligus
    actions = ['delete_selected']

# Daftarkan model CleaningLog ke admin
admin.site.register(CleaningLog, CleaningLogAdmin)
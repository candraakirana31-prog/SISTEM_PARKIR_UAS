# SISTEM_PARKIR_UAS

## Deploy ke Vercel dan Supabase

Proyek ini sudah memiliki entrypoint Flask untuk Vercel pada `api/index.py`.

1. Buat project PostgreSQL di Supabase.
2. Salin connection string Supabase dari menu **Connect**. Gunakan connection pooler jika koneksi langsung bermasalah.
3. Di Vercel, import repository ini dan tambahkan environment variables berikut:

	```env
	DATABASE_URL=postgresql://...
	SECRET_KEY=ganti-dengan-string-acak-yang-panjang
	NAMA_KAMPUS=Universitas Bale Bandung
	```

4. Deploy project. Vercel akan menggunakan `vercel.json` dan `api/index.py` untuk menjalankan Flask.
5. Untuk membuat tabel dan akun admin pada database Supabase, jalankan seed sekali dari komputer lokal dengan `DATABASE_URL` Supabase yang sama:

	```powershell
	$env:DATABASE_URL = "postgresql://..."
	python seed.py
	```

Login admin default setelah seed:

- Username: `CandraKIrana`
- Password: `CandraKirana31`

Ganti password default setelah login pertama. Jangan memasukkan `DATABASE_URL` atau `SECRET_KEY` ke repository.
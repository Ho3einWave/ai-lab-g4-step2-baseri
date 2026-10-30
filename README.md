# گام دوم آزمایشگاه هوش مصنوعی — مستندسازی منبع و ساختار داده

- **گروه:** ۴
- **موضوع پروژه:** تشخیص ژانر موسیقی
- **نقش در این گام:** مستندات
- **تسک:** مستند کردن منبع و ساختار داده

## مخزن‌های گام دوم گروه

| نقش | تسک | مخزن |
|---|---|---|
| طراحی | تعیین منبع داده و بررسی مجوز | [ghorbannerzhad](https://github.com/legend-hassan/ai-lab-g4-step2-ghorbannerzhad) |
| کد | اسکریپت بارگذاری داده یا ساخت محیط | [veiseh](https://github.com/Veiseh/ai-lab-g4-step2-veiseh) |
| داده و ارزیابی | پاک‌سازی و جدا کردن مجموعه آزمون | [EhsanHeydari](https://github.com/ehsanheydariwww/ai-lab-g4-step2-EhsanHeydari) |
| مستندات | مستند کردن منبع و ساختار داده | همین مخزن |

## خلاصه

| مورد | مقدار |
|---|---|
| دیتاست | GTZAN Genre Collection (Tzanetakis و Cook، ۲۰۰۲) |
| نسخه استفاده‌شده | [storylinez/gtzan-music-genre-dataset](https://huggingface.co/datasets/storylinez/gtzan-music-genre-dataset) در Hugging Face |
| تعداد قطعه در نسخه اصلی | ۱۰۰۰ قطعه، ۱۰ ژانر، ۱۰۰ قطعه برای هر ژانر |
| تعداد قطعه در نسخه Hugging Face | **۸۶۰** (۱۴۰ قطعه کم است، با وجود اینکه صفحه آن ۱۰۰۰ اعلام کرده) |
| داده فعلی گروه | ۱۴ قطعه از ۵ ژانر (۱۰ آموزش، ۴ آزمون) |
| مشخصات صوت | WAV، ۲۲۰۵۰ هرتز، تک‌کاناله، ۱۶ بیتی، ۳۰ ثانیه (برای هر ۱۴ فایل بررسی شد) |
| برچسب‌گذاری | نام پوشه هر فایل = ژانر آن |
| مجوز | صفحه Hugging Face مجوز MIT اعلام کرده، ولی صوت‌ها حق نشر دارند و فقط برای استفاده آموزشی و پژوهشی مناسب‌اند |

## مستندات

- [`docs/data_source.md`](docs/data_source.md) — منبع داده، نسخه استفاده‌شده، مجوز، مشکلات شناخته‌شده GTZAN، ارجاع، و مقایسه با FMA که بخش طراحی پیشنهاد داده بود
- [`docs/data_structure.md`](docs/data_structure.md) — مسیر داده بین اعضای گروه، ساختار پوشه‌ها، قاعده نام‌گذاری، مشخصات فنی صوت‌ها، توزیع داده و فرهنگ داده (توضیح ستون‌های همه فایل‌های CSV و JSON)

## اسکریپت‌ها

هر دو اسکریپت فقط از کتابخانه‌های استاندارد پایتون استفاده می‌کنند و نصب کتابخانه لازم ندارند.

| فایل | کار | خروجی |
|---|---|---|
| `src/inspect_audio.py` | خواندن مشخصات فنی هر فایل صوتی (نرخ نمونه‌برداری، کانال، عمق بیت، طول، حجم، SHA-256) و مقایسه با مشخصات GTZAN | `data/audio_inventory.csv`، `data/audio_summary.json` |
| `src/mirror_inventory.py` | گرفتن فهرست فایل‌های نسخه Hugging Face (بدون دانلود صوت) و پیدا کردن قطعه‌های کم در هر ژانر | `data/mirror_inventory.csv`، `data/mirror_summary.json` |

### اجرا

```bash
# مشخصات فایل‌های صوتی؛ مسیر پوشه genres_original مخزن کد را بدهید
python src/inspect_audio.py --audio-root ../ai-lab-g4-step2-veiseh/data/genres_original

# فهرست فایل‌های نسخه Hugging Face (اینترنت لازم است)
python src/mirror_inventory.py
```

خروجی اجرا:

```text
Files: 14  Genres: {'blues': 3, 'classical': 2, 'hiphop': 5, 'jazz': 1, 'rock': 3}
Sample rates: [22050]  Channels: [1]  Bit depths: [16]
Duration min/max: 30.0/30.013 s
Files with issues: 0

Mirror files: 860 of 1000
  blues      present= 80  missing= 20
  classical  present= 82  missing= 18
  country    present= 91  missing=  9
  disco      present= 85  missing= 15
  hiphop     present= 91  missing=  9
  jazz       present= 90  missing= 10
  metal      present= 82  missing= 18
  pop        present= 86  missing= 14
  reggae     present= 84  missing= 16
  rock       present= 89  missing= 11
```

## نکاتی برای هماهنگی گروه

موارد زیر هنگام مستندسازی پیدا شد و برای گام بعد پیشنهاد می‌شود:

1. **منبع داده یکسان نیست:** بخش طراحی FMA را پیشنهاد کرده، ولی بخش کد و ارزیابی با GTZAN کار کرده‌اند. پیشنهاد: ادامه با GTZAN و ثبت این تصمیم در گزارش گروه (جزئیات در `docs/data_source.md` بخش ۶).
2. **نسخه Hugging Face ناقص است:** ۸۶۰ قطعه به‌جای ۱۰۰۰. اگر کل دیتاست لازم شد، باید از نسخه کامل (مثلاً Kaggle) دانلود شود یا این کمبود در گزارش ذکر شود.
3. **مسیرهای ویندوزی:** `metadata.csv` مخزن کد مسیر کامل ویندوزی دارد و روی سیستم‌های دیگر کار نمی‌کند. بهتر است `load_data.py` مسیر نسبی ذخیره کند.
4. **فایل‌های صوتی در گیت‌هاب:** ۱۴ فایل WAV در مخزن عمومی کد قرار گرفته‌اند. به دلیل حق نشر بهتر است حذف و در `.gitignore` قرار گیرند.
5. **محل `requirements.txt`:** در مخزن کد این فایل در پوشه `reports/` است، ولی راهنمای اجرا آن را در پوشه اصلی فرض می‌کند.
6. **داده کم:** فقط ۵ ژانر از ۱۰ ژانر و جاز با یک نمونه؛ برای ارزیابی معنادار باید داده بیشتری دانلود شود.

## ساختار مخزن

```
.
├── README.md
├── docs/
│   ├── data_source.md        منبع داده و مجوز
│   └── data_structure.md     ساختار داده و فرهنگ داده
├── src/
│   ├── inspect_audio.py      بررسی مشخصات فایل‌های صوتی
│   └── mirror_inventory.py   فهرست فایل‌های نسخه Hugging Face
└── data/
    ├── audio_inventory.csv   مشخصات هر ۱۴ فایل صوتی
    ├── audio_summary.json    خلاصه مشخصات صوتی
    ├── mirror_inventory.csv  فهرست ۸۶۰ فایل نسخه Hugging Face
    └── mirror_summary.json   تعداد موجود و غایب در هر ژانر
```

فایل‌های صوتی در این مخزن قرار نمی‌گیرند.

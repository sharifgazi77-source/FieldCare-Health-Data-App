FIELDCARE — স্বাস্থ্য ডেটা এন্ট্রি অ্যাপ

সহজে চালানোর নিয়ম (Windows)
1. ZIP ফাইলটি Extract All করে একটি ফোল্ডারে খুলুন।
2. ওই ফোল্ডারের ফাঁকা জায়গায় Shift চেপে Right-click করে “Open PowerShell window here” নির্বাচন করুন।
3. লিখুন: py -m venv .venv
4. লিখুন: .venv\Scripts\activate
5. লিখুন: pip install -r requirements.txt
6. লিখুন: py app.py
7. ব্রাউজারে খুলুন: http://127.0.0.1:5000

পরেরবার চালাতে শুধু ফোল্ডারে PowerShell খুলে লিখুন:
.venv\Scripts\activate
py app.py

ডেটা fieldcare.db ফাইলে, একই ফোল্ডারেই সংরক্ষিত থাকে। লোকাল SQLite ডিফল্ট হওয়ায় আলাদা সার্ভার সেটআপ লাগে না। CSV ডাউনলোড বাটনে Excel-এ খোলার উপযোগী রিপোর্ট পাবেন। PostgreSQL ব্যবহার করতে PowerShell-এ চালানোর আগে DATABASE_URL সেট করুন, উদাহরণ:
$env:DATABASE_URL = "postgresql://postgres:আপনারপাসওয়ার্ড@localhost:5432/fieldcare"
py app.py
আগে PostgreSQL-এ fieldcare নামে একটি database তৈরি করুন।

গুরুত্বপূর্ণ: এটি এক কম্পিউটারে স্থানীয় ব্যবহারের জন্য। রোগীর সংবেদনশীল তথ্য রাখার আগে প্রতিষ্ঠানের গোপনীয়তা ও ব্যাকআপ নীতিমালা মেনে চলুন। অ্যাপটি ইন্টারনেটে প্রকাশ করবেন না।

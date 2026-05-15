Login lấy token 
```bash
curl -X POST http://localhost:8080/comic/auth/login \
     -H "Content-Type: application/json" \
     -d '{
           "email": "hlklonga5@gmail.com",
           "password": "Long1234"
         }'
```

```bash
$body = @{
    email = "hlklonga5@gmail.com"
    password = "Long1234"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/comic/auth/login" `
      -Method Post `
      -ContentType "application/json" `
      -Body $body
```

Tạo comic mới
```bash
curl -X POST "http://localhost:8080/comic/comics" \
  -H "Authorization: Bearer eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJobGtsb25nYTVAZ21haWwuY29tIiwiaWF0IjoxNzc4ODQxNjIyLCJleHAiOjE3Nzg5MjgwMjJ9.-4cWodAFdJrvgXZyivVNZjNl3PBrnVZQo_oNFk3H77lbm9qLggSsjT4m6JoTGX27" \
  -F "title=Mayonaka no Heartune" \
  -F "description=Thánh Yamabuki và dàn harem" \
  -F "author=Masakuni Igarashi" \
  -F "originalLanguage=ja" \
  -F "format=MANGA" \
  -F "status=ONGOING" \
  -F "genres=4" \
  -F "genres=6" \
  -F "genres=10" \
  -F "coverImage=@/d/uet/_duan/code/manga-pipeline/tests/assets/mayonaka/c1/0000.jpg"
```

```bash
$token = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJobGtsb25nYTVAZ21haWwuY29tIiwiaWF0IjoxNzc4ODQxNjIyLCJleHAiOjE3Nzg5MjgwMjJ9.-4cWodAFdJrvgXZyivVNZjNl3PBrnVZQo_oNFk3H77lbm9qLggSsjT4m6JoTGX27"

$headers = @{
    "Authorization" = "Bearer $token"
}

# Lưu ý: Cần sử dụng PowerShell 6+ để tham số -Form hoạt động
$form = @{
    title = "Mayonaka no Heartune"
    description = "Thánh Yamabuki và dàn harem"
    author = "Masakuni Igarashi"
    originalLanguage = "ja"
    format = "MANGA"
    status = "ONGOING"
    genres = "4,6,10"
    coverImage = Get-Item -Path "D:\uet\_duan\code\manga-pipeline\tests\assets\mayonaka\c1\0000.jpg"
}

Invoke-WebRequest -Uri "http://localhost:8080/comic/comics" -Method Post -Headers $headers -Form $form
```

Tạo chapter mới
```bash
curl -X POST "http://localhost:8080/comic/comics/6/chapters" \
  -H "Authorization: Bearer eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJobGtsb25nYTVAZ21haWwuY29tIiwiaWF0IjoxNzc4ODQxNjIyLCJleHAiOjE3Nzg5MjgwMjJ9.-4cWodAFdJrvgXZyivVNZjNl3PBrnVZQo_oNFk3H77lbm9qLggSsjT4m6JoTGX27" \
  -H "Content-Type: application/json" \
  -d '{
    "chapterNumber": 1,
    "title": "RE:START"
  }'
```

Upload chapter pages
```bash
curl -X POST "http://localhost:8080/comic/chapters/11/pages?startPageNumber=1&targetLangs=vi&targetLangs=en" \
  -H "Authorization: Bearer eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJobGtsb25nYTVAZ21haWwuY29tIiwiaWF0IjoxNzc4ODQxNjIyLCJleHAiOjE3Nzg5MjgwMjJ9.-4cWodAFdJrvgXZyivVNZjNl3PBrnVZQo_oNFk3H77lbm9qLggSsjT4m6JoTGX27" \
  -F "files=@D:\uet\_duan\code\manga-pipeline\tests\assets\mayonaka\c1\0008.jpg" \
  -F "files=@D:\uet\_duan\code\manga-pipeline\tests\assets\mayonaka\c1\0009.jpg" \
  -F "files=@D:\uet\_duan\code\manga-pipeline\tests\assets\mayonaka\c1\0010.jpg"
```


GetAnnouncements – Duyuru Listesi

Endpoint

GET /api/MetroMobile/V2/GetAnnouncements/{Language}

Parametre
	•	Language: TR | EN | AR (zorunlu)

Body

Yok.

cURL

curl -sS "https://api.ibb.gov.tr/MetroIstanbul/api/MetroMobile/V2/GetAnnouncements/TR"

Response (özet)

{
  "Success": true,
  "Error": null,
  "Data": [
    {
      "Id": 627,
      "Title": "Duyuru Başlığı",
      "Content": "<p>HTML içerik</p>",
      "StartDate": "2025-12-14T00:01:00",
      "Photo": "https://...",
      "Media": { "Video": null, "Images": [] }
    }
  ]
}



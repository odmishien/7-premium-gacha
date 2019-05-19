package main

import (
	"database/sql"
	"html/template"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/lib/pq"
)

type Product struct {
	Id           int
	ProductName  string
	Genre        string
	SubGenre     string
	Price        int
	PriceWithTax int
}

type Data struct {
	Products     []Product
	Total        int
	TotalWithTax int
}

func indexHTMLHandler(w http.ResponseWriter, r *http.Request) {
	t := template.Must(template.ParseFiles("templates/index.html"))

	if err := t.ExecuteTemplate(w, "index.html", nil); err != nil {
		log.Fatal(err)
	}
}

func gachaHTMLHandler(w http.ResponseWriter, r *http.Request) {
	var total int
	var genre []string
	var result_total int
	var result_total_with_tax int
	var data Data

	tmpls, _ := template.ParseFiles("templates/index.html")
	tmpl := tmpls.Lookup("index.html")

	r.ParseForm()
	total_str := r.FormValue("total")
	genre = r.Form["genre[]"]
	total, _ = strconv.Atoi(total_str)

	products := getProductsList(total, genre)

	for _, p := range products {
		result_total = result_total + p.Price
		result_total_with_tax = result_total_with_tax + p.PriceWithTax
	}

	data.Products = products
	data.Total = result_total
	data.TotalWithTax = result_total_with_tax

	if err := tmpl.Execute(w, data); err != nil {
		log.Fatal(err)
	}
}

func getProductsList(total int, genre []string) []Product {
	var candidateproducts []Product
	var products []Product

	db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Fatal(err)
	}

	rows, err := db.Query(`SELECT * FROM "seven_premium_products" WHERE (price_with_tax <= $1) AND genre ~~* ANY($2)`, total, pq.Array(genre))
	if err != nil {
		log.Fatal(err)
	}

	for rows.Next() {
		var p Product
		if err := rows.Scan(&p.Id, &p.ProductName, &p.Genre, &p.SubGenre, &p.Price, &p.PriceWithTax); err != nil {
			log.Fatal(err)
		}
		candidateproducts = append(candidateproducts, p)
	}

	retry_count := 0
	for {
		selected_product := getRandomElementFromProductsList(candidateproducts)
		if selected_product.PriceWithTax < total {
			products = append(products, selected_product)
			total = total - selected_product.PriceWithTax
			retry_count = 0
		} else {
			retry_count = retry_count + 1
			if retry_count > 30 {
				break
			}
		}
	}
	return products
}

func getRandomElementFromProductsList(products []Product) Product {
	rand.Seed(time.Now().UnixNano())
	i := rand.Intn(len(products))
	return products[i]
}

func main() {
	http.HandleFunc("/", indexHTMLHandler)
	http.HandleFunc("/gacha", gachaHTMLHandler)

	if err := http.ListenAndServe(":8000", nil); err != nil {
		panic(err)
	}
}

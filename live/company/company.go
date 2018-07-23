package company

import (
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

var Companies []Company

type Company struct {
	gorm.Model
	Symbol   string `gorm:"type:varchar(10)"`
	Name     string `gorm:"type:varchar(50)"`
	Segment  string `gorm:"type:varchar(200)"`
	Ibovespa bool
}

func (Company) TableName() string {
	return "bovespa_company"
}

func StartDatabase() *gorm.DB {
	dbUrl := "host=localhost port=5432 dbname=xt user=postgres password=postgres sslmode=disable"
	db, err := gorm.Open("postgres", dbUrl)
	if err != nil {
		panic(err)
	}

	db.AutoMigrate(&Company{})
	db.Where("ibovespa = true").Order("segment desc").Find(&Companies)
	return db
}

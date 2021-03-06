// Binary app_engine_go111_data is an example Go App Engine application.
package main

import (
	"fmt"
	"net/http"

	"google.golang.org/appengine"
	"google.golang.org/appengine/user"

	"example.com/mypkg" // This dep is in gopath rather than app directory
)

func main() {
	http.HandleFunc("/", handler)
	appengine.Main()
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, Go World! ")
	// [START new_context]
	c := appengine.NewContext(r)
	// [END new_context]
	// [START get_current_user]
	u := user.Current(c)
	// [END get_current_user]
	// [START if_user]
	if u == nil {
		url, err := user.LoginURL(c, r.URL.String())
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Location", url)
		w.WriteHeader(http.StatusFound)
		return
	}
	// [END if_user]
	// [START output]
	fmt.Fprintf(w, "Hello, %v! ", u)
	fmt.Fprintf(w, "%v", mypkg.HelloNotags)
	// [END output]
}

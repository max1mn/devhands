package handlers

import (
	"net/http"
)

func Static(w http.ResponseWriter, r *http.Request) {
	// fmt.Fprint(w, `{"message": Hello, world!"}`)
	// fmt.Fprint(w, "Hello, world!")
	JSONResponse(w, MessageResponse{"Hello, world!"})
}

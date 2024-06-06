package handlers

import (
	"net/http"
)

func Ok(w http.ResponseWriter, r *http.Request) {
	JSONResponse(w, MessageResponse{"ok"})
}

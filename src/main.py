from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from sqladmin import Admin

from .admin import AdminAuth, AdminCookieMiddleware, UserAdmin, RoomAdmin, BookingAdmin

from .config import settings
from .database import engine
from .lifespan import lifespan

from .auth.router import auth_router
from .users.router import user_router
from .rooms.router import room_router
from .bookings.router import booking_router


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)
app.add_middleware(AdminCookieMiddleware)

routers = [
    auth_router,
    user_router,
    room_router,
    booking_router,
]

for router in routers:
    app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <a href="http://127.0.0.1:8000/docs">Documentation</a><br>
    <a href="http://127.0.0.1:8000/redoc">ReDoc</a>
    """


admin = Admin(
    app,
    engine,
    authentication_backend=AdminAuth(),
)

views = [
    UserAdmin,
    RoomAdmin,
    BookingAdmin,
]

for view in views:
    admin.add_view(view)

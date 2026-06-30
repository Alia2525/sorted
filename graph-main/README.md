# ArticleDz

API для статей на Django REST Framework з JWT-автентифікацією, permissions, фільтрацією, пошуком та підготовкою до деплою.

## Можливості

- `/api/articles/` - CRUD для статей.
- `/api/comments/` - CRUD для коментарів.
- `/api/auth/register/` - реєстрація користувача.
- `/api/auth/login/` - отримання JWT access/refresh token.
- `/api/auth/refresh/` - оновлення access token.
- Публічне читання статей.
- Публічне читання коментарів.
- Створення статей тільки для авторизованих користувачів.
- Створення коментарів тільки для авторизованих користувачів.
- Редагування статті тільки автором або admin/staff.
- Редагування коментаря тільки автором або admin/staff.
- Видалення статей і коментарів тільки admin/staff.
- Повноцінне відображення зв'язку моделей: стаття повертається разом зі списком вкладених коментарів.
- Пошук за `title` і `content`.
- Фільтрація за `category` і `author`.
- Сортування за `created_at`.

## Моделі та зв'язки

У проєкті є дві основні моделі:

- `Article` - стаття.
- `Comment` - коментар до статті.

Зв'язок між ними:

- одна стаття має багато коментарів;
- один коментар належить одній статті;
- зв'язок реалізовано через `ForeignKey` у моделі `Comment`;
- для зручного populate використано `related_name="comments"`.

У відповіді `/api/articles/` кожна стаття повертається разом із вкладеним списком `comments`.

Приклад відповіді:

```json
{
  "id": 1,
  "title": "Django REST Framework",
  "content": "Article text",
  "category": "Django",
  "author": "admin",
  "created_at": "2026-06-20T10:00:00Z",
  "comments": [
    {
      "id": 1,
      "article": 1,
      "author": "reader",
      "text": "Nice article",
      "created_at": "2026-06-20T10:05:00Z"
    }
  ]
}
```

## Permissions

У проєкті реалізовано кастомний permission:

- `IsAuthorOrAdminOrReadOnly` - дозволяє читати статті й коментарі всім, а змінювати тільки автору або адміністратору.

Також використано стандартний permission:

- `IsAdminUser` - видалення статей і коментарів доступне тільки адміністраторам.

Permissions підключені в `ArticleViewSet` і `CommentViewSet`.

## Локальний запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Для Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Налаштування `.env`

Файл `.env` створюється локально на основі `.env.example` і не додається в репозиторій.

Основні змінні:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `ACCESS_TOKEN_LIFETIME_MINUTES`
- `REFRESH_TOKEN_LIFETIME_DAYS`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## API

### Articles

- `GET /api/articles/` - список статей.
- `POST /api/articles/` - створення статті, потрібен JWT token.
- `GET /api/articles/{id}/` - перегляд статті.
- `PATCH /api/articles/{id}/` - редагування статті автором або admin.
- `DELETE /api/articles/{id}/` - видалення статті тільки admin.

Статті повертаються з вкладеним полем `comments`.

### Comments

- `GET /api/comments/` - список коментарів.
- `POST /api/comments/` - створення коментаря, потрібен JWT token.
- `GET /api/comments/{id}/` - перегляд коментаря.
- `PATCH /api/comments/{id}/` - редагування коментаря автором або admin.
- `DELETE /api/comments/{id}/` - видалення коментаря тільки admin.

Приклад авторизованого запиту:

```bash
curl -H "Authorization: Bearer <access_token>" http://127.0.0.1:8000/api/articles/
```

### Auth

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

## Деплой

Додано GitHub Actions workflow:

- `.github/workflows/deploy.yml`

Для роботи workflow потрібно додати в GitHub repository secrets:

- `HOST`
- `USERNAME`
- `SSH_PRIVATE_KEY`
- `PROJECT_PATH`

На VPS потрібно:

- зклонувати репозиторій;
- створити `.env` на основі `.env.example`;
- створити віртуальне середовище;
- встановити залежності з `requirements.txt`;
- виконати `python manage.py migrate`;
- виконати `python manage.py collectstatic --noinput`;
- налаштувати Gunicorn через `systemd`;
- налаштувати Nginx як reverse proxy;
- підключити домен і HTTPS через Certbot.

Шаблони для сервера:

- `deploy/systemd/article-dz.service`
- `deploy/systemd/article-dz.socket`
- `deploy/nginx/article-dz.conf`

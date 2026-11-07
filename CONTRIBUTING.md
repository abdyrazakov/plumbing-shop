# Как работать над проектом вместе (GitHub)

Проект: https://github.com/abdyrazakov/plumbing-shop
Основная ветка: `master`. Она всегда должна быть рабочей.

---

## 1. Получить доступ

**Вариант А — collaborator (рекомендуется).** Владелец добавляет тебя в репозиторий:

- Web: `Settings` → `Collaborators` → `Add people` → ввести username → роль `Write`.
- CLI (владелец):

```bash
gh api -X PUT repos/abdyrazakov/plumbing-shop/collaborators/USERNAME -f permission=push
```

После этого прими приглашение на GitHub (письмо или `https://github.com/abdyrazakov/plumbing-shop/invitations`).

**Вариант Б — fork.** Если доступа нет: нажми `Fork`, работай в своём форке и открывай PR в исходный репозиторий.

---

## 2. Первый запуск

```bash
git clone https://github.com/abdyrazakov/plumbing-shop.git
cd plumbing-shop

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python seed_demo.py                # демо-данные (пересоздаёт категории/товары/заказы)
python manage.py createsuperuser   # свой аккаунт для /admin/
python manage.py runserver
```

Проверь, что тесты проходят:

```bash
python manage.py test
```

---

## 3. Правила веток

- **Никогда не коммить напрямую в `master`.**
- Одна задача = одна ветка = один PR.
- Имена веток:

```
design/home-redesign
design/product-page
fix/cart-total
docs/readme
```

Создать ветку:

```bash
git checkout master
git pull origin master
git checkout -b design/home-redesign
```

---

## 4. Коммиты

Пиши коротко и по делу, в одном стиле:

```
design: переработана главная и hero-блок
design: карточки товаров — единый аспект и бейдж наличия
fix: неверный итог корзины при количестве 0
docs: инструкция для команды
```

Не коммить:

- `db.sqlite3`, `media/`, `.venv/`, `*.log` — они в `.gitignore`;
- чужие незавершённые файлы;
- секреты, токены, пароли.

Проверить, что попадёт в коммит:

```bash
git status
git diff
```

---

## 5. Публикация и Pull Request

```bash
git add .
git commit -m "design: переработана главная"
git push -u origin design/home-redesign
```

Дальше на GitHub нажми **Compare & pull request**. В описании PR укажи:

- что сделано и зачем;
- скриншоты «до/после» (десктоп + мобильный);
- что проверено (`python manage.py test`, ручной проход страниц);
- что осталось или требует решения владельца.

Шаблон:

```md
## Что сделано
- Переработан hero на главной
- Карточки категорий переведены на SVG

## Скриншоты
(до/после, mobile/desktop)

## Проверка
- [ ] python manage.py test — 59 passed
- [ ] 360/768/1440 px
- [ ] prefers-reduced-motion

## Требует решения
- Нужны id товаров для блока «Популярное» — без правки views не обойтись
```

---

## 6. Ревью и merge

1. Владелец (или второй участник) смотрит PR: код, скриншоты, поведение.
2. Правки — новыми коммитами в ту же ветку, не новым PR.
3. После апрува — **Squash and merge**, затем `Delete branch`.
4. Перед merge убедись, что PR не отстал от `master` (см. ниже).

---

## 7. Синхронизация с master

Если `master` ушёл вперёд, а твоя ветка старая:

```bash
git checkout master
git pull origin master
git checkout design/home-redesign
git rebase master
```

Если после rebase есть конфликты:

```bash
git status                  # список конфликтных файлов
# открой файлы, реши конфликты, убери маркеры <<<<<<< ======= >>>>>>>
git add <файл>
git rebase --continue
```

Отменить rebase и вернуться как было:

```bash
git rebase --abort
```

После rebase ветку нужно запушить с `--force-with-lease` (только в свою ветку!):

```bash
git push --force-with-lease
```

---

## 8. Что можно и нельзя менять

Можно: шаблоны, CSS, статику, документацию.

Нельзя без согласования: `views.py`, `models.py`, `forms.py`, `cart.py`, `urls.py`, `settings.py`, миграции, `requirements.txt`, `tests.py`.

Если нужны данные, которых нет в шаблоне, — опиши это в PR, не добавляй сам.

Если нашёл баг бэкенда — отдельный issue с шагами воспроизведения:

```
1. Открыть /cart/
2. Добавить 2 товара
3. Ожидалось: итог 1000
4. Фактически: итог 500
```

---

## 9. Защита `master` (настраивает владелец)

GitHub → `Settings` → `Branches` → `Add branch protection rule`:

- Branch name pattern: `master`
- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale approvals when new commits are pushed
- ✅ Require status checks to pass (если настроен CI)
- ✅ Do not allow bypassing the above settings

Для маленькой команды достаточно первых двух пунктов.

---

## 10. Чек-лист перед PR

- [ ] Ветка создана от свежего `master`.
- [ ] `python manage.py test` — все тесты зелёные.
- [ ] `python manage.py check` — без ошибок.
- [ ] Проверено на 360, 768, 1024, 1440 px.
- [ ] Нет изменений бэкенда без согласования.
- [ ] Нет `db.sqlite3`, `media/`, `.venv/`, логов в коммите.
- [ ] Скриншоты до/после приложены.
- [ ] Описание PR заполнено.

---

## 11. Полезные команды

```bash
git status                     # что изменено
git log --oneline -10          # последние коммиты
git diff                       # изменения до add
git diff --staged              # изменения после add
git restore <файл>             # отменить правки в файле
git switch -c <ветка>          # создать и перейти
git pull --rebase origin master
gh pr create --fill            # создать PR из терминала
gh pr view --web               # открыть PR в браузере
```

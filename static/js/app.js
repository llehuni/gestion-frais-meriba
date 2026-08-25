// ===== NAVIGATION =====
        const titles = {
            dashboard: 'Tableau de bord',
            students: 'Élèves',
            classes: 'Classes',
            years: 'Années scolaires',
            fees: 'Frais scolaires',
            payments: 'Paiements',
            receipts: 'Reçus',
            reports: 'Rapports',
            users: 'Utilisateurs',
            audit: "Journal d'audit"
        };

        function go(page) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + page).classList.add('active');
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            const link = document.querySelector(`.nav-item[data-page="${page}"]`);
            if (link) link.classList.add('active');
            document.getElementById('crumb').textContent = titles[page] || page;
            document.getElementById('sidebar').classList.remove('open');
            closeAllDropdowns();
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
        }

        // ===== LOGIN =====
        function handleLogin(e) {
            e.preventDefault();
            const role = document.getElementById('role').value;
            const map = {
                admin: { name: 'Admin', init: 'AD' },
                secretaire: { name: 'Mme Kabuya', init: 'MK' },
                caissier: { name: 'M. Tshibangu', init: 'TT' },
                directeur: { name: 'M. Mukendi', init: 'DM' }
            };
            document.getElementById('uName').textContent = map[role].name;
            document.getElementById('uAvatar').textContent = map[role].init;
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('app').classList.add('active');
        }

        function logout() {
            document.getElementById('app').classList.remove('active');
            document.getElementById('loginPage').style.display = 'flex';
        }

        // ===== DROPDOWNS =====
        function toggleDropdown(event, btn) {
            event.stopPropagation();
            const dropdown = btn.parentElement;
            const wasOpen = dropdown.classList.contains('open');
            closeAllDropdowns();
            if (!wasOpen) dropdown.classList.add('open');
        }

        function closeAllDropdowns() {
            document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));
        }

        // Close dropdowns on outside click
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.dropdown')) closeAllDropdowns();
        });

        // Close dropdowns on escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeAllDropdowns();
                document.querySelectorAll('.modal-bg.active').forEach(m => m.classList.remove('active'));
            }
        });

        // ===== MODALS =====
        function openModal(id) {
            closeAllDropdowns();
            document.getElementById(id).classList.add('active');
        }
        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        document.querySelectorAll('.modal-bg').forEach(m => {
            m.addEventListener('click', e => { if (e.target === m) m.classList.remove('active'); });
        });

        // ===== TABS =====
        function switchTab(btn, targetId) {
            btn.parentElement.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('ft-types').style.display = targetId === 'ft-types' ? 'block' : 'none';
            document.getElementById('ft-amounts').style.display = targetId === 'ft-amounts' ? 'block' : 'none';
        }

        // ===== TOAST =====
        function toast(msg, type = 'success') {
            closeAllDropdowns();
            const c = document.getElementById('toasts');
            const t = document.createElement('div');
            t.className = 'toast' + (type === 'error' ? ' error' : type === 'warning' ? ' warning' : '');
            const icons = { success: 'fa-check-circle', error: 'fa-circle-exclamation', warning: 'fa-triangle-exclamation' };
            t.innerHTML = `<i class="fas ${icons[type]}" style="color:${type === 'error' ? 'var(--danger)' : type === 'warning' ? 'var(--warning)' : 'var(--success)'}"></i><span>${msg}</span>`;
            c.appendChild(t);
            setTimeout(() => {
                t.style.opacity = '0';
                t.style.transform = 'translateX(100%)';
                t.style.transition = 'all 0.2s';
                setTimeout(() => t.remove(), 200);
            }, 2800);
        }

        // ===== FORMS =====
        function submitStudent() {
            closeModal('m-student');
            toast('Élève enregistré — Matricule MER-2024-248');
        }
        function submitPayment() {
            closeModal('m-payment');
            toast('Paiement enregistré — Reçu REC-2025-0143');
        }

        // ===== PAGINATION =====
        function paginate(btn, direction) {
            const container = btn.closest('.page-btns');
            const btns = container.querySelectorAll('.page-btn');
            let activeIdx = -1;
            btns.forEach((b, i) => { if (b.classList.contains('active')) activeIdx = i; });

            if (direction === -1) {
                if (activeIdx > 1) {
                    btns[activeIdx].classList.remove('active');
                    btns[activeIdx - 1].classList.add('active');
                }
            } else if (direction === 1) {
                if (activeIdx < btns.length - 2) {
                    btns[activeIdx].classList.remove('active');
                    btns[activeIdx + 1].classList.add('active');
                }
            } else {
                btns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            }
            toast('Page mise à jour');
        }

        // ===== ACTION HANDLERS =====
        let pendingAction = null;

        function actionView(type, id) {
            closeAllDropdowns();
            toast(`Ouverture de la fiche : ${type} ${id}`);
        }

        function actionEdit(type, id) {
            closeAllDropdowns();
            toast(`Modification : ${type} ${id}`);
        }

        function actionDelete(type, id) {
            closeAllDropdowns();
            pendingAction = { type: 'delete', entity: type, id: id };
            document.getElementById('confirm-title').textContent = `Supprimer ce ${type} ?`;
            document.getElementById('confirm-message').textContent = `Êtes-vous sûr de vouloir supprimer ${type} « ${id} » ? Cette action est irréversible.`;
            document.getElementById('confirm-btn').textContent = 'Supprimer';
            openModal('m-confirm');
        }

        function actionPay(id) {
            closeAllDropdowns();
            openModal('m-payment');
            toast(`Préparation du paiement pour ${id}`);
        }

        function actionReceipt(id) {
            closeAllDropdowns();
            document.getElementById('receipt-title').textContent = id;
            document.getElementById('receipt-num').textContent = id;
            openModal('m-receipt');
        }

        function actionPrint(id) {
            closeAllDropdowns();
            toast(`Impression du reçu ${id}`);
        }

        function actionBlock(login) {
            closeAllDropdowns();
            pendingAction = { type: 'block', id: login };
            document.getElementById('confirm-title').textContent = 'Bloquer le compte ?';
            document.getElementById('confirm-message').textContent = `L'utilisateur « ${login} » ne pourra plus se connecter. Voulez-vous continuer ?`;
            document.getElementById('confirm-btn').textContent = 'Bloquer';
            openModal('m-confirm');
        }

        function actionUnblock(login) {
            closeAllDropdowns();
            toast(`Compte « ${login} » réactivé`);
        }

        function confirmAction() {
            closeModal('m-confirm');
            if (!pendingAction) return;
            if (pendingAction.type === 'delete') {
                toast(`${pendingAction.entity} « ${pendingAction.id} » supprimé`);
            } else if (pendingAction.type === 'block') {
                toast(`Compte « ${pendingAction.id} » bloqué`);
            }
            pendingAction = null;
        }

        // ===== RESPONSIVE =====
        window.addEventListener('resize', () => {
            if (window.innerWidth > 900) document.getElementById('sidebar').classList.remove('open');
        });

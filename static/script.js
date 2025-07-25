/**
 * نظام إدارة العقارات - JavaScript Application
 */

// متغيرات عامة
let currentProperties = [];
let currentPropertyId = null;
let refreshInterval = null;
let systemStatus = 'unknown';

// تهيئة التطبيق
function initializeApp() {
    console.log('🏠 تهيئة نظام إدارة العقارات...');
    
    // تحديث الوقت
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // تحميل البيانات الأولية
    loadInitialData();
    
    // بدء التحديث التلقائي
    startAutoRefresh();
    
    // إعداد مستمعي الأحداث
    setupEventListeners();
    
    console.log('✅ تم تهيئة النظام بنجاح');
}

// تحديث الوقت الحالي
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleString('ar-SA', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// تحميل البيانات الأولية
async function loadInitialData() {
    try {
        showLoading(true);
        
        // تحميل الإحصائيات
        await loadSystemStats();
        
        // تحميل العقارات
        await loadProperties();
        
        // فحص حالة النظام
        await checkSystemHealth();
        
    } catch (error) {
        console.error('❌ خطأ في تحميل البيانات:', error);
        showToast('خطأ في تحميل البيانات', 'error');
    } finally {
        showLoading(false);
    }
}

// تحميل إحصائيات النظام
async function loadSystemStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('فشل في تحميل الإحصائيات');
        
        const stats = await response.json();
        updateStatsDisplay(stats);
        
    } catch (error) {
        console.error('❌ خطأ في تحميل الإحصائيات:', error);
    }
}

// تحديث عرض الإحصائيات
function updateStatsDisplay(stats) {
    const elements = {
        'total-properties': stats.total_properties || 0,
        'successful-properties': stats.status_counts?.['عقار ناجح'] || 0,
        'pending-properties': stats.status_counts?.['قيد المعالجة'] || 0,
        'failed-properties': stats.status_counts?.['عقار فاشل'] || 0
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            // تأثير العد التصاعدي
            animateCounter(element, value);
        }
    });
    
    // تحديث حالة النظام
    systemStatus = stats.system_status;
    updateSystemStatusDisplay();
}

// تأثير العد التصاعدي
function animateCounter(element, targetValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const increment = Math.ceil((targetValue - currentValue) / 20);
    
    if (currentValue < targetValue) {
        element.textContent = currentValue + increment;
        setTimeout(() => animateCounter(element, targetValue), 50);
    } else {
        element.textContent = targetValue;
    }
}

// تحميل العقارات
async function loadProperties(status = '', limit = 50, offset = 0) {
    try {
        const params = new URLSearchParams({
            limit: limit.toString(),
            offset: offset.toString()
        });
        
        if (status) {
            params.append('status', status);
        }
        
        const response = await fetch(`/api/properties?${params}`);
        if (!response.ok) throw new Error('فشل في تحميل العقارات');
        
        const data = await response.json();
        currentProperties = data.properties;
        displayProperties(currentProperties);
        
    } catch (error) {
        console.error('❌ خطأ في تحميل العقارات:', error);
        showNoDataMessage();
    }
}

// عرض العقارات في الجدول
function displayProperties(properties) {
    const tbody = document.getElementById('properties-table-body');
    const noDataMessage = document.getElementById('no-data-message');
    
    if (!properties || properties.length === 0) {
        tbody.innerHTML = '';
        noDataMessage.style.display = 'block';
        return;
    }
    
    noDataMessage.style.display = 'none';
    
    tbody.innerHTML = properties.map(property => `
        <tr class="fade-in" data-property-id="${property.id}">
            <td data-label="المعرف">${property.id}</td>
            <td data-label="البيان" class="text-truncate-2" style="max-width: 200px;" title="${property.البيان || 'غير محدد'}">
                ${property.البيان || 'غير محدد'}
            </td>
            <td data-label="المنطقة">${property.المنطقة || 'غير محدد'}</td>
            <td data-label="نوع الوحدة">${property['نوع الوحدة'] || 'غير محدد'}</td>
            <td data-label="المالك">${property['اسم المالك'] || 'غير محدد'}</td>
            <td data-label="السعر">${formatPrice(property.السعر)} جنيه</td>
            <td data-label="الحالة">${getStatusBadge(property.status)}</td>
            <td data-label="تاريخ الإنشاء">${formatDateTime(property.created_at)}</td>
            <td data-label="الإجراءات">
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewPropertyDetails(${property.id})" title="عرض التفاصيل">
                        <i data-feather="eye"></i>
                    </button>
                    ${property.status === 'عقار فاشل' || property.status === 'قيد المعالجة' ? `
                        <button class="btn btn-outline-warning" onclick="reprocessProperty(${property.id})" title="إعادة المعالجة">
                            <i data-feather="refresh-cw"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
    
    // إعادة تهيئة الأيقونات
    feather.replace();
}

// تنسيق السعر
function formatPrice(price) {
    if (!price || price === '0') return '0';
    const numPrice = parseInt(price);
    return new Intl.NumberFormat('ar-SA').format(numPrice);
}

// تنسيق التاريخ والوقت
function formatDateTime(dateTimeString) {
    if (!dateTimeString) return 'غير محدد';
    
    const date = new Date(dateTimeString);
    return date.toLocaleString('ar-SA', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// إنشاء شارة الحالة
function getStatusBadge(status) {
    const statusMap = {
        'عقار جديد': { class: 'status-new', icon: 'plus-circle' },
        'عقار ناجح': { class: 'status-success', icon: 'check-circle' },
        'قيد المعالجة': { class: 'status-pending', icon: 'clock' },
        'عقار فاشل': { class: 'status-failed', icon: 'x-circle' },
        'عقار مكرر': { class: 'status-duplicate', icon: 'copy' },
        'عقار متعدد': { class: 'status-multiple', icon: 'layers' }
    };
    
    const statusInfo = statusMap[status] || { class: 'status-new', icon: 'help-circle' };
    
    return `
        <span class="status-badge ${statusInfo.class}">
            <i data-feather="${statusInfo.icon}"></i>
            ${status}
        </span>
    `;
}

// عرض تفاصيل العقار
async function viewPropertyDetails(propertyId) {
    try {
        currentPropertyId = propertyId;
        
        const response = await fetch(`/api/property/${propertyId}`);
        if (!response.ok) throw new Error('فشل في تحميل تفاصيل العقار');
        
        const property = await response.json();
        displayPropertyDetails(property);
        
        // عرض النافذة المنبثقة
        const modal = new bootstrap.Modal(document.getElementById('propertyModal'));
        modal.show();
        
    } catch (error) {
        console.error('❌ خطأ في تحميل تفاصيل العقار:', error);
        showToast('خطأ في تحميل تفاصيل العقار', 'error');
    }
}

// عرض تفاصيل العقار في النافذة المنبثقة
function displayPropertyDetails(property) {
    const detailsContainer = document.getElementById('property-details');
    
    const details = [
        { label: 'المعرف', value: property.id },
        { label: 'البيان', value: property.البيان },
        { label: 'المنطqة', value: property.المنطقة },
        { label: 'كود الوحدة', value: property['كود الوحدة'] },
        { label: 'نوع الوحدة', value: property['نوع الوحدة'] },
        { label: 'حالة الوحدة', value: property['حالة الوحدة'] },
        { label: 'المساحة', value: property.المساحة ? `${property.المساحة} متر مربع` : '' },
        { label: 'الدور', value: property.الدور },
        { label: 'السعر', value: property.السعر ? `${formatPrice(property.السعر)} جنيه` : '' },
        { label: 'المميزات', value: property.المميزات },
        { label: 'العنوان', value: property.العنوان },
        { label: 'اسم الموظف', value: property['اسم الموظف'] },
        { label: 'اسم المالك', value: property['اسم المالك'] },
        { label: 'رقم المالك', value: property['رقم المالك'] },
        { label: 'إتاحة العقار', value: property['اتاحة العقار'] },
        { label: 'حالة الصور', value: property['حالة الصور'] },
        { label: 'الحالة', value: getStatusBadge(property.status) },
        { label: 'تاريخ الإنشاء', value: formatDateTime(property.created_at) },
        { label: 'آخر تحديث', value: formatDateTime(property.updated_at) },
        { label: 'محاولات المعالجة', value: property.processing_attempts || 0 }
    ];
    
    detailsContainer.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                ${details.slice(0, Math.ceil(details.length / 2)).map(item => 
                    item.value ? `
                        <div class="property-detail-item">
                            <span class="property-detail-label">${item.label}:</span>
                            <span class="property-detail-value">${item.value}</span>
                        </div>
                    ` : ''
                ).join('')}
            </div>
            <div class="col-md-6">
                ${details.slice(Math.ceil(details.length / 2)).map(item => 
                    item.value ? `
                        <div class="property-detail-item">
                            <span class="property-detail-label">${item.label}:</span>
                            <span class="property-detail-value">${item.value}</span>
                        </div>
                    ` : ''
                ).join('')}
            </div>
        </div>
        
        ${property['تفاصيل كاملة'] ? `
            <div class="mt-3">
                <h6>تفاصيل كاملة:</h6>
                <div class="border p-3 rounded bg-light">
                    ${property['تفاصيل كاملة']}
                </div>
            </div>
        ` : ''}
        
        ${property.error_messages && property.error_messages.length > 0 ? `
            <div class="mt-3">
                <h6 class="text-danger">رسائل الخطأ:</h6>
                <div class="alert alert-danger">
                    <ul class="mb-0">
                        ${property.error_messages.map(msg => `<li>${msg}</li>`).join('')}
                    </ul>
                </div>
            </div>
        ` : ''}
        
        <div class="mt-3">
            <h6>الروابط الخارجية:</h6>
            <div class="d-flex gap-2 flex-wrap">
                ${property.notion_property_id ? `
                    <a href="https://www.notion.so/${property.notion_property_id.replace(/-/g, '')}" 
                       target="_blank" class="btn btn-sm btn-outline-primary">
                        <i data-feather="external-link" class="me-1"></i>
                        صفحة العقار في Notion
                    </a>
                ` : ''}
                ${property.notion_owner_id ? `
                    <a href="https://www.notion.so/${property.notion_owner_id.replace(/-/g, '')}" 
                       target="_blank" class="btn btn-sm btn-outline-info">
                        <i data-feather="external-link" class="me-1"></i>
                        صفحة المالك في Notion
                    </a>
                ` : ''}
                ${property.zoho_lead_id ? `
                    <a href="https://crm.zoho.com/crm/EntityInfo?module=Leads&id=${property.zoho_lead_id}" 
                       target="_blank" class="btn btn-sm btn-outline-success">
                        <i data-feather="external-link" class="me-1"></i>
                        العميل في Zoho CRM
                    </a>
                ` : ''}
            </div>
        </div>
    `;
    
    // إعادة تهيئة الأيقونات
    feather.replace();
}

// إعادة معالجة العقار
async function reprocessProperty(propertyId = null) {
    const id = propertyId || currentPropertyId;
    if (!id) return;
    
    try {
        const response = await fetch(`/api/property/${id}/reprocess`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('فشل في إعادة المعالجة');
        
        const result = await response.json();
        showToast('تم طلب إعادة المعالجة بنجاح', 'success');
        
        // إغلاق النافذة المنبثقة إذا كانت مفتوحة
        const modal = bootstrap.Modal.getInstance(document.getElementById('propertyModal'));
        if (modal) modal.hide();
        
        // تحديث البيانات
        setTimeout(() => {
            loadProperties();
            loadSystemStats();
        }, 1000);
        
    } catch (error) {
        console.error('❌ خطأ في إعادة المعالجة:', error);
        showToast('خطأ في إعادة المعالجة', 'error');
    }
}

// التحكم في النظام
async function controlSystem(action) {
    try {
        const response = await fetch(`/api/system/${action}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error(`فشل في ${action === 'start' ? 'تشغيل' : 'إيقاف'} النظام`);
        
        const result = await response.json();
        showToast(result.message, 'success');
        
        // تحديث حالة النظام
        setTimeout(checkSystemHealth, 1000);
        
    } catch (error) {
        console.error(`❌ خطأ في ${action === 'start' ? 'تشغيل' : 'إيقاف'} النظام:`, error);
        showToast(`خطأ في ${action === 'start' ? 'تشغيل' : 'إيقاف'} النظام`, 'error');
    }
}

// فحص صحة النظام
async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();
        
        systemStatus = response.ok ? health.processor : 'غير متصل';
        updateSystemStatusDisplay();
        
    } catch (error) {
        console.error('❌ خطأ في فحص صحة النظام:', error);
        systemStatus = 'غير متصل';
        updateSystemStatusDisplay();
    }
}

// تحديث عرض حالة النظام
function updateSystemStatusDisplay() {
    const statusElement = document.getElementById('system-status');
    if (!statusElement) return;
    
    const statusMap = {
        'يعمل': { class: 'bg-success', text: 'النظام يعمل', icon: 'check-circle' },
        'متوقف': { class: 'bg-warning', text: 'النظام متوقف', icon: 'pause-circle' },
        'غير متصل': { class: 'bg-danger', text: 'غير متصل', icon: 'x-circle' }
    };
    
    const status = statusMap[systemStatus] || statusMap['غير متصل'];
    
    statusElement.className = `badge ${status.class} text-white`;
    statusElement.innerHTML = `
        <i data-feather="${status.icon}" class="me-1"></i>
        ${status.text}
    `;
    
    feather.replace();
}

// فلترة العقارات حسب الحالة
function filterProperties() {
    const statusFilter = document.getElementById('status-filter').value;
    loadProperties(statusFilter);
}

// البحث في العقارات
function searchProperties() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
    
    if (!searchTerm) {
        displayProperties(currentProperties);
        return;
    }
    
    const filteredProperties = currentProperties.filter(property => {
        return Object.values(property).some(value => {
            if (value && typeof value === 'string') {
                return value.toLowerCase().includes(searchTerm);
            }
            return false;
        });
    });
    
    displayProperties(filteredProperties);
}

// تحديث البيانات
async function refreshData() {
    const refreshBtn = document.querySelector('[onclick="refreshData()"]');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i data-feather="refresh-cw" class="spinner-border spinner-border-sm me-1"></i> جاري التحديث...';
    }
    
    try {
        await loadInitialData();
        showToast('تم تحديث البيانات', 'success');
    } catch (error) {
        showToast('خطأ في تحديث البيانات', 'error');
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i data-feather="refresh-cw" class="me-1"></i> تحديث البيانات';
            feather.replace();
        }
    }
}

// بدء التحديث التلقائي
function startAutoRefresh() {
    // تحديث كل 30 ثانية
    refreshInterval = setInterval(() => {
        loadSystemStats();
        checkSystemHealth();
    }, 30000);
}

// إيقاف التحديث التلقائي
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// عرض/إخفاء مؤشر التحميل
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    const noDataMessage = document.getElementById('no-data-message');
    
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
    
    if (!show && noDataMessage) {
        noDataMessage.style.display = 'none';
    }
}

// عرض رسالة عدم وجود بيانات
function showNoDataMessage() {
    const noDataMessage = document.getElementById('no-data-message');
    if (noDataMessage) {
        noDataMessage.style.display = 'block';
    }
}

// عرض التوست (الإشعارات)
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    if (!toast || !toastMessage) return;
    
    // تحديد نوع الإشعار
    const typeMap = {
        'success': { class: 'text-success', icon: 'check-circle' },
        'error': { class: 'text-danger', icon: 'x-circle' },
        'warning': { class: 'text-warning', icon: 'alert-triangle' },
        'info': { class: 'text-info', icon: 'info' }
    };
    
    const toastType = typeMap[type] || typeMap['info'];
    
    // تحديث محتوى التوست
    toastMessage.innerHTML = `
        <i data-feather="${toastType.icon}" class="me-2 ${toastType.class}"></i>
        ${message}
    `;
    
    // عرض التوست
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // إعادة تهيئة الأيقونات
    feather.replace();
}

// إعداد مستمعي الأحداث
function setupEventListeners() {
    // مستمع تغيير حجم الشاشة
    window.addEventListener('resize', function() {
        // إعادة تهيئة الجداول المتجاوبة إذا لزم الأمر
    });
    
    // مستمع الضغط على مفاتيح لوحة المفاتيح للبحث السريع
    document.addEventListener('keydown', function(event) {
        // Ctrl+F للبحث
        if (event.ctrlKey && event.key === 'f') {
            event.preventDefault();
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // F5 للتحديث
        if (event.key === 'F5') {
            event.preventDefault();
            refreshData();
        }
    });
    
    // مستمع إغلاق النافذة
    window.addEventListener('beforeunload', function() {
        stopAutoRefresh();
    });
}

// تصدير الدوال للاستخدام العام
window.RealEstateApp = {
    initializeApp,
    loadProperties,
    viewPropertyDetails,
    reprocessProperty,
    controlSystem,
    refreshData,
    filterProperties,
    searchProperties
};

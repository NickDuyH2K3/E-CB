// iframe-widget.js
(function() {
    var container = document.querySelector('[id^="ecb-chatbot-"]');
    var config = JSON.parse(container.getAttribute('data-ecb-config'));
    config.embedStyle = 'inline';
    var allowedDomains = JSON.parse(container.getAttribute('data-ecb-allowed-domains'));
    var cdn = JSON.parse(container.getAttribute('data-ecb-cdn'));

    // Load the widget SDK
    var script = document.createElement('script');
    script.src = cdn + '/widget.min.js';
    script.onload = function() {
        new ECBWidget(config);
    };
    document.head.appendChild(script);

    // Prevent iframe from being embedded in suspicious domains
    if (window.top !== window.self) {
        var parentDomain = document.referrer ? (new window.URL(document.referrer)).hostname : '';
        if (allowedDomains[0] !== '*' && allowedDomains.indexOf(parentDomain) === -1) {
            document.body.innerHTML = '<div style="padding: 20px; text-align: center;">Access denied: Domain not authorized</div>';
        }
    }
})(); 
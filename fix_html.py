with open('wbs-api/frontend/index.html', encoding='utf-8') as f:
    content = f.read()

# Normalize to LF
content = content.replace('\r\n', '\n')

# Replace manager field
content = content.replace(
    '                <select id="project_manager"><option value="">Select manager...</option></select>\n                <div class="inline-add">\n                  <input type="text" id="new_manager" placeholder="Add new manager" />\n                  <button class="btn-add" type="button" onclick="addManager()">+ Add</button>\n                </div>',
    '                <div class="smart-list" id="manager_list"></div>\n                <div class="smart-add" id="manager_add" style="display:none;">\n                  <input type="text" id="new_manager" placeholder="Enter manager name" />\n                  <button class="btn-add" type="button" onclick="confirmAddManager()">Save</button>\n                  <button class="btn-cancel" type="button" onclick="hideAdd(\'manager\')">Cancel</button>\n                </div>'
)

# Replace recipients field
content = content.replace(
    '                <div class="multi-select" id="recipient_list"></div>\n                <div class="inline-add">\n                  <input type="email" id="new_recipient" placeholder="Add email" />\n                  <button class="btn-add" type="button" onclick="addEmail(\'recipient\')">+ Add</button>\n                </div>',
    '                <div class="smart-list" id="recipient_list"></div>\n                <div class="smart-add" id="recipient_add" style="display:none;">\n                  <input type="email" id="new_recipient" placeholder="Enter email" />\n                  <button class="btn-add" type="button" onclick="confirmAddEmail(\'recipient\')">Save</button>\n                  <button class="btn-cancel" type="button" onclick="hideAdd(\'recipient\')">Cancel</button>\n                </div>'
)

# Replace CC field
content = content.replace(
    '                <div class="multi-select" id="cc_list"></div>\n                <div class="inline-add">\n                  <input type="email" id="new_cc" placeholder="Add email" />\n                  <button class="btn-add" type="button" onclick="addEmail(\'cc\')">+ Add</button>\n                </div>',
    '                <div class="smart-list" id="cc_list"></div>\n                <div class="smart-add" id="cc_add" style="display:none;">\n                  <input type="email" id="new_cc" placeholder="Enter email" />\n                  <button class="btn-add" type="button" onclick="confirmAddEmail(\'cc\')">Save</button>\n                  <button class="btn-cancel" type="button" onclick="hideAdd(\'cc\')">Cancel</button>\n                </div>'
)

with open('wbs-api/frontend/index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print('smart-list in content:', 'smart-list' in content)
print('multi-select remaining:', 'multi-select' in content)
print('inline-add remaining:', 'inline-add' in content)

-- 1. 사용자 관리: Users 테이블
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- 해시값 권장
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'participant',  -- 예: 'creator' 또는 'participant'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 공모전 관리: Contests 테이블 (제공된 구조 활용)
CREATE TABLE contests (
    contest_id INT AUTO_INCREMENT PRIMARY KEY,
    keywords VARCHAR(255),
    title VARCHAR(255),
    company VARCHAR(255),
    due_date VARCHAR(50),   -- 필요에 따라 DATE 타입 사용 고려
    view_count INT,
    thumbnail_url VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 모임 관리: Meetings 테이블
CREATE TABLE meetings (
    meeting_id INT AUTO_INCREMENT PRIMARY KEY,
    contest_id INT NOT NULL,               -- 관련 공모전 (Contests와 연관)
    description TEXT,                      -- 모임 상세 설명
    subject VARCHAR(255),                  -- 모임 주제
    capacity INT,                          -- 인원 제한
    creator_id INT NOT NULL,               -- 모임 생성자 (Users와 연관)
    approval_status VARCHAR(20) DEFAULT 'pending', -- full or pending
    share_link VARCHAR(255),               -- 공유 링크 (카카오톡, 슬랙 등)
    current_participants INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contest_id) REFERENCES Contests(contest_id),
    FOREIGN KEY (creator_id) REFERENCES Users(user_id)
);

-- 4. 모임 참여 및 평가: MeetingParticipants 테이블
CREATE TABLE meeting_participants (
    meeting_id INT NOT NULL,
    user_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- 예: 'pending', 'approved', 'rejected'
    evaluation_score FLOAT,                -- 모임 종료 후 평가 점수 (평가가 없으면 NULL)
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (meeting_id, user_id),
    FOREIGN KEY (meeting_id) REFERENCES Meetings(meeting_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 5. 활동 이력 관리: ActivityHistory 테이블
--    activity_type: 'login', 'contest_activity' 등으로 구분
--    로그인 이력에 IP주소, 로그인일시와 로그아웃일시를 기록할 수 있도록 logout_time 컬럼 추가
CREATE TABLE activity_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,    -- 예: 'login', 'contest_activity'
    activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,              -- 로그아웃일시 (로그아웃 시 업데이트)
    details TEXT,                          -- 추가 설명 (예: 로그인 성공 여부 등)
    ip_address VARCHAR(45),                -- IP주소 기록 (IPv6 포함)
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
